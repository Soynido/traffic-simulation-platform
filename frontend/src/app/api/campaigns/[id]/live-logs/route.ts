import { NextRequest, NextResponse } from 'next/server';

// Use Docker service name for backend communication
const BACKEND_URL = 'http://backend:8000/api/v1';

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const { searchParams } = new URL(request.url);
    const since = searchParams.get('since');
    const limit = searchParams.get('limit') || '50';

    let url = `${BACKEND_URL}/campaigns/${params.id}/live-logs?limit=${limit}`;
    if (since) {
      url += `&since=${encodeURIComponent(since)}`;
    }

    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Backend responded with ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error fetching live logs:', error);
    return NextResponse.json(
      { error: 'Failed to fetch live logs' },
      { status: 500 }
    );
  }
}