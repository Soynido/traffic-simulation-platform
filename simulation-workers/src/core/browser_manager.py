"""
Browser Manager for Traffic Simulation

Manages Playwright browser instances for web automation
with proper resource management and error handling.
"""

import asyncio
import os
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager

from playwright.async_api import async_playwright, Browser, BrowserContext, Page
import structlog

logger = structlog.get_logger(__name__)


class BrowserManager:
    """Manages browser instances and contexts for simulation."""
    
    def __init__(
        self,
        headless: bool = True,
        browser_type: str = "chromium",
        max_contexts: int = 10,
        timeout_ms: int = 30000
    ):
        self.headless = headless
        self.browser_type = browser_type
        self.max_contexts = max_contexts
        self.timeout_ms = timeout_ms
        
        self._playwright = None
        self._browser = None
        self._active_contexts: Dict[str, BrowserContext] = {}
        self._semaphore = asyncio.Semaphore(max_contexts)
        
    async def initialize(self) -> None:
        """Initialize Playwright and browser."""
        try:
            logger.info("Initializing browser manager", browser_type=self.browser_type)
            
            self._playwright = await async_playwright().start()
            
            # Get browser type
            browser_launcher = getattr(self._playwright, self.browser_type)
            
            # Launch browser with configuration
            self._browser = await browser_launcher.launch(
                headless=self.headless,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--disable-features=VizDisplayCompositor",
                ] if self.headless else []
            )
            
            logger.info("Browser manager initialized successfully")
            
        except Exception as e:
            logger.error("Failed to initialize browser manager", error=str(e))
            raise
    
    async def cleanup(self) -> None:
        """Clean up all browser resources."""
        try:
            logger.info("Cleaning up browser manager")
            
            # Close all active contexts
            for context_id, context in self._active_contexts.items():
                try:
                    await context.close()
                    logger.debug("Closed context", context_id=context_id)
                except Exception as e:
                    logger.warning("Error closing context", context_id=context_id, error=str(e))
            
            self._active_contexts.clear()
            
            # Close browser
            if self._browser:
                await self._browser.close()
                
            # Stop playwright
            if self._playwright:
                await self._playwright.stop()
                
            logger.info("Browser manager cleanup completed")
            
        except Exception as e:
            logger.error("Error during browser cleanup", error=str(e))
    
    @asynccontextmanager
    async def get_context(
        self, 
        context_id: str,
        user_agent: Optional[str] = None,
        viewport: Optional[Dict[str, int]] = None,
        extra_http_headers: Optional[Dict[str, str]] = None
    ):
        """Get a browser context with resource management."""
        async with self._semaphore:
            context = None
            try:
                logger.debug("Creating browser context", context_id=context_id)
                
                # Create new context
                context_options = {
                    "user_agent": user_agent,
                    "viewport": viewport or {"width": 1920, "height": 1080},
                    "extra_http_headers": extra_http_headers or {},
                }
                
                # Remove None values
                context_options = {k: v for k, v in context_options.items() if v is not None}
                
                context = await self._browser.new_context(**context_options)
                self._active_contexts[context_id] = context
                
                # Set default timeout
                context.set_default_timeout(self.timeout_ms)
                
                yield context
                
            except Exception as e:
                logger.error("Error in browser context", context_id=context_id, error=str(e))
                raise
            finally:
                # Clean up context
                if context and context_id in self._active_contexts:
                    try:
                        await context.close()
                        del self._active_contexts[context_id]
                        logger.debug("Context closed", context_id=context_id)
                    except Exception as e:
                        logger.warning("Error closing context", context_id=context_id, error=str(e))
    
    async def get_page(self, context: BrowserContext) -> Page:
        """Create a new page in the given context."""
        page = await context.new_page()
        
        # Set default timeout for page operations
        page.set_default_timeout(self.timeout_ms)
        
        return page
    
    def get_browser_info(self) -> Dict[str, Any]:
        """Get browser information."""
        return {
            "browser_type": self.browser_type,
            "headless": self.headless,
            "max_contexts": self.max_contexts,
            "timeout_ms": self.timeout_ms,
            "active_contexts": len(self._active_contexts),
            "is_connected": self._browser is not None and self._browser.is_connected()
        }