import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    const backendUrl = process.env.API_URL || 'http://backend:8000/api/v1';
    console.log('Backend URL:', backendUrl);
    
    const response = await fetch(`${backendUrl}/campaigns`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    console.log('Response status:', response.status);
    console.log('Response headers:', Object.fromEntries(response.headers.entries()));

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Backend error response:', errorText);
      throw new Error(`Backend responded with ${response.status}: ${errorText}`);
    }

    const data = await response.json();
    console.log('Backend response data:', data);
    return NextResponse.json({ success: true, data, backendUrl });
  } catch (error) {
    console.error('Error in test API route:', error);
    return NextResponse.json(
      { 
        error: 'Failed to fetch campaigns', 
        details: error instanceof Error ? error.message : String(error),
        backendUrl: process.env.API_URL || 'http://backend:8000/api/v1'
      },
      { status: 500 }
    );
  }
}
