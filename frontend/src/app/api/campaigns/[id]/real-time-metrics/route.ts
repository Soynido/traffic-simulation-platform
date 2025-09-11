import { NextRequest, NextResponse } from 'next/server';

// Use Docker service name for backend communication
const BACKEND_URL = 'http://backend:8000/api/v1';

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const url = `${BACKEND_URL}/campaigns/${params.id}/real-time-metrics`;

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
    console.error('Error fetching real-time metrics:', error);
    return NextResponse.json(
      { error: 'Failed to fetch real-time metrics' },
      { status: 500 }
    );
  }
}