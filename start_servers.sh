#!/bin/bash

# Stop existing servers
echo "🛑 Stopping existing servers..."
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:5173 | xargs kill -9 2>/dev/null
lsof -ti:5174 | xargs kill -9 2>/dev/null
sleep 1

# Start Backend
echo "🚀 Starting Backend Server..."
cd /Users/awwy/writing_system_backend
python3 manage.py runserver 0.0.0.0:8000 > /tmp/django_server.log 2>&1 &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"
echo "   Logs: tail -f /tmp/django_server.log"

# Wait for backend to start
sleep 3
if curl -s http://localhost:8000/api/v1/ > /dev/null 2>&1; then
    echo "   ✅ Backend is running at http://localhost:8000"
else
    echo "   ⚠️  Backend may still be starting..."
fi

# Start Frontend
echo ""
echo "🚀 Starting Frontend Server..."
cd /Users/awwy/writing_system_frontend
npm run dev > /tmp/vite_server.log 2>&1 &
FRONTEND_PID=$!
echo "   Frontend PID: $FRONTEND_PID"
echo "   Logs: tail -f /tmp/vite_server.log"

# Wait for frontend to start
sleep 4
PORT=$(grep -o "Local:.*http://localhost:[0-9]*" /tmp/vite_server.log 2>/dev/null | grep -o "[0-9]*" | head -1)
if [ ! -z "$PORT" ]; then
    echo "   ✅ Frontend is running at http://localhost:$PORT"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "✅ Both servers are running!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "📡 Backend:  http://localhost:8000"
    echo "🎨 Frontend: http://localhost:$PORT"
    echo "🔗 Signup:   http://localhost:$PORT/signup"
    echo ""
    echo "📋 View logs:"
    echo "   Backend:  tail -f /tmp/django_server.log"
    echo "   Frontend: tail -f /tmp/vite_server.log"
    echo ""
    echo "🛑 To stop servers:"
    echo "   kill $BACKEND_PID $FRONTEND_PID"
else
    echo "   ⚠️  Frontend may still be starting. Check logs above."
fi

