import React, { useState, useEffect, useCallback, useRef } from 'react';

const OptimizedRealTimePlotbot = () => {
  // State management
  const [timeSeriesData, setTimeSeriesData] = useState([]);
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackSpeed, setPlaybackSpeed] = useState(1);
  const [selectedPoint, setSelectedPoint] = useState(null);
  const [showVDF, setShowVDF] = useState(false);
  const [vdfData, setVdfData] = useState([]);
  const [scrubPosition, setScrubPosition] = useState(null);
  const [audioFrequency, setAudioFrequency] = useState(440);
  const [isAudioPlaying, setIsAudioPlaying] = useState(false);
  const [audioWindow, setAudioWindow] = useState(false);
  
  // Range selection state
  const [isRangeSelectionMode, setIsRangeSelectionMode] = useState(false);
  const [rangeStartTime, setRangeStartTime] = useState(null);
  const [rangeEndTime, setRangeEndTime] = useState(null);
  const [zoomRange, setZoomRange] = useState(null);
  const [originalRange, setOriginalRange] = useState(null);
  const [isShiftPressed, setIsShiftPressed] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [dragStartX, setDragStartX] = useState(null);
  const [currentDragX, setCurrentDragX] = useState(null);
  
  // Refs
  const mainCanvasRef = useRef(null);
  const vdfCanvasRef = useRef(null);
  const intervalRef = useRef(null);
  const audioContextRef = useRef(null);
  const oscillatorRef = useRef(null);
  const gainNodeRef = useRef(null);
  const animationRef = useRef(null);
  
  // Constants
  const windowSize = 500;
  const canvasWidth = 800;
  const canvasHeight = 500; // Made taller for axes
  
  // Data buffers
  const dataBuffer = useRef(new Float32Array(windowSize * 4));
  const timeBuffer = useRef(new Float32Array(windowSize));
  const dataIndex = useRef(0);
  const lastDrawTime = useRef(0); // Force redraw tracking
  
  // Initialize data
  useEffect(() => {
    for (let i = 0; i < windowSize; i++) {
      const t = i * 0.01;
      timeBuffer.current[i] = Date.now() + i * 100;
      dataBuffer.current[i * 4] = 5 * Math.sin(t) + Math.random() - 0.5;
      dataBuffer.current[i * 4 + 1] = 3 * Math.cos(t * 1.2) + Math.random() - 0.5;
      dataBuffer.current[i * 4 + 2] = 2 * Math.sin(t * 0.8) + Math.random() - 0.5;
      dataBuffer.current[i * 4 + 3] = Math.sqrt(
        Math.pow(dataBuffer.current[i * 4], 2) + 
        Math.pow(dataBuffer.current[i * 4 + 1], 2) + 
        Math.pow(dataBuffer.current[i * 4 + 2], 2)
      );
    }
    dataIndex.current = windowSize;
  }, []);
  
  // Keyboard handlers
  useEffect(() => {
    const handleKeyDown = (event) => {
      if (event.key === 'Shift' && !isShiftPressed) {
        setIsShiftPressed(true);
        setIsRangeSelectionMode(true);
      } else if (event.key === 'Escape') {
        resetZoom();
      }
    };
    
    const handleKeyUp = (event) => {
      if (event.key === 'Shift') {
        setIsShiftPressed(false);
        setIsRangeSelectionMode(false);
        setRangeStartTime(null);
        setRangeEndTime(null);
      }
    };
    
    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('keyup', handleKeyUp);
    
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('keyup', handleKeyUp);
    };
  }, [isShiftPressed]);
  
  // Get visible data range
  const getVisibleRange = useCallback(() => {
    if (zoomRange) {
      // zoomRange now contains data indices directly
      const startIdx = Math.max(0, zoomRange.start);
      const endIdx = Math.min(windowSize - 1, zoomRange.end);
      return { start: startIdx, end: endIdx, count: endIdx - startIdx };
    }
    return { start: 0, end: windowSize - 1, count: windowSize };
  }, [zoomRange]);
  
  // HSL to RGB conversion
  const hslToRgb = (h, s, l) => {
    const c = (1 - Math.abs(2 * l - 1)) * s;
    const x = c * (1 - Math.abs((h * 6) % 2 - 1));
    const m = l - c / 2;
    let r, g, b;
    
    if (h < 1/6) [r, g, b] = [c, x, 0];
    else if (h < 2/6) [r, g, b] = [x, c, 0];
    else if (h < 3/6) [r, g, b] = [0, c, x];
    else if (h < 4/6) [r, g, b] = [0, x, c];
    else if (h < 5/6) [r, g, b] = [x, 0, c];
    else [r, g, b] = [c, 0, x];
    
    return [(r + m) * 255, (g + m) * 255, (b + m) * 255];
  };
  
  // Draw main plot
  const drawMainPlot = useCallback(() => {
    const canvas = mainCanvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    
    // Clear
    ctx.fillStyle = '#1a1a1a';
    ctx.fillRect(0, 0, width, height);
    
    // Grid
    ctx.strokeStyle = '#333';
    ctx.lineWidth = 1;
    for (let i = 0; i < 10; i++) {
      const y = (height / 10) * i;
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
      ctx.stroke();
    }
    
    const colors = ['#22c55e', '#f97316', '#3b82f6', '#000000'];
    const labels = ['B_R', 'B_T', 'B_N', '|B|'];
    
    const visibleRange = getVisibleRange();
    const dataStart = visibleRange.start;
    const dataEnd = visibleRange.end;
    const dataCount = visibleRange.count;
    
    // Draw each component
    for (let comp = 0; comp < 4; comp++) {
      ctx.strokeStyle = colors[comp];
      ctx.lineWidth = comp === 3 ? 3 : 2;
      ctx.beginPath();
      
      let minVal = Infinity, maxVal = -Infinity;
      for (let i = dataStart; i <= dataEnd; i++) {
        const val = dataBuffer.current[i * 4 + comp];
        minVal = Math.min(minVal, val);
        maxVal = Math.max(maxVal, val);
      }
      
      const range = maxVal - minVal || 1;
      
      for (let i = dataStart; i < dataEnd; i++) {
        const x1 = ((i - dataStart) / dataCount) * width;
        const x2 = ((i + 1 - dataStart) / dataCount) * width;
        
        const val1 = dataBuffer.current[i * 4 + comp];
        const val2 = dataBuffer.current[(i + 1) * 4 + comp];
        
        const y1 = height - ((val1 - minVal) / range) * height * 0.8 - height * 0.1;
        const y2 = height - ((val2 - minVal) / range) * height * 0.8 - height * 0.1;
        
        if (i === dataStart) ctx.moveTo(x1, y1);
        ctx.lineTo(x2, y2);
      }
      ctx.stroke();
    }
    
    // Debug info overlay
    ctx.fillStyle = '#ffffff';
    ctx.font = '10px monospace';
    ctx.fillText(`Data range: ${dataStart} - ${dataEnd} (showing ${dataCount} of ${windowSize} points)`, 10, height - 110);
    ctx.fillText(`Canvas: ${width}x${height} pixels`, 10, height - 100);
    
    // Add visual markers at the data boundaries to help debug
    if (zoomRange) {
      // Draw markers showing where the data boundaries should be
      const leftPixel = 0; // Data starts at left edge of zoomed view
      const rightPixel = width; // Data ends at right edge of zoomed view
      
      ctx.strokeStyle = '#ff00ff';
      ctx.lineWidth = 2;
      ctx.setLineDash([2, 2]);
      
      // Left boundary
      ctx.beginPath();
      ctx.moveTo(leftPixel, 0);
      ctx.lineTo(leftPixel, height);
      ctx.stroke();
      
      // Right boundary  
      ctx.beginPath();
      ctx.moveTo(rightPixel, 0);
      ctx.lineTo(rightPixel, height);
      ctx.stroke();
      
      ctx.setLineDash([]);
      
      ctx.fillStyle = '#ff00ff';
      ctx.font = '8px monospace';
      ctx.fillText(`Data boundaries`, 10, height - 50);
      ctx.fillText(`Should match your selection`, 10, height - 40);
    }
    
    // Draw zoom preview overlay when zoomed
    if (zoomRange) {
      ctx.fillStyle = 'rgba(0, 255, 255, 0.1)';
      ctx.fillRect(0, 0, width, height);
      
      ctx.strokeStyle = '#00ffff';
      ctx.lineWidth = 2;
      ctx.setLineDash([3, 3]);
      ctx.strokeRect(0, 0, width, height);
      ctx.setLineDash([]);
      
      ctx.fillStyle = '#00ffff';
      ctx.font = '12px monospace';
      ctx.fillText(`🔍 ZOOMED`, width - 100, 20);
      ctx.fillText(`Data indices: ${dataStart} - ${dataEnd}`, 10, height - 30);
      ctx.fillText(`Zoom range: ${zoomRange.start} - ${zoomRange.end}`, 10, height - 20);
    }
    
    // Draw drag selection
    if (isDragging && dragStartX !== null && currentDragX !== null) {
      const left = Math.min(dragStartX, currentDragX);
      const right = Math.max(dragStartX, currentDragX);
      
      ctx.fillStyle = 'rgba(255, 255, 0, 0.3)';
      ctx.fillRect(left, 0, right - left, height);
      
      ctx.strokeStyle = '#ffff00';
      ctx.lineWidth = 2;
      ctx.setLineDash([3, 3]);
      ctx.strokeRect(left, 0, right - left, height);
      ctx.setLineDash([]);
      
      ctx.strokeStyle = '#ffff00';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(dragStartX, 0);
      ctx.lineTo(dragStartX, height);
      ctx.stroke();
      
      ctx.strokeStyle = '#ff6600';
      ctx.beginPath();
      ctx.moveTo(currentDragX, 0);
      ctx.lineTo(currentDragX, height);
      ctx.stroke();
    }
    
    // Selected point indicator with data values
    if (selectedPoint) {
      const x = selectedPoint.x;
      ctx.strokeStyle = '#00ff00';
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, height);
      ctx.stroke();
      
      // Show selected point data
      ctx.fillStyle = '#00ff00';
      ctx.font = '10px monospace';
      ctx.fillText(`Selected Point [${selectedPoint.dataIndex}]:`, x + 5, 20);
      ctx.fillText(`Br: ${selectedPoint.br?.toFixed(2)} nT`, x + 5, 35);
      ctx.fillText(`Bt: ${selectedPoint.bt?.toFixed(2)} nT`, x + 5, 50);
      ctx.fillText(`Bn: ${selectedPoint.bn?.toFixed(2)} nT`, x + 5, 65);
      ctx.fillText(`|B|: ${selectedPoint.bmag?.toFixed(2)} nT`, x + 5, 80);
    }
    
    // Scrub line
    if (scrubPosition && !isDragging) {
      ctx.strokeStyle = '#ff0000';
      ctx.lineWidth = 2;
      ctx.setLineDash([5, 5]);
      ctx.beginPath();
      ctx.moveTo(scrubPosition, 0);
      ctx.lineTo(scrubPosition, height);
      ctx.stroke();
      ctx.setLineDash([]);
    }
    
    // Legend
    ctx.fillStyle = '#ffffff';
    ctx.font = '14px monospace';
    for (let i = 0; i < labels.length; i++) {
      ctx.fillStyle = colors[i];
      ctx.fillText(labels[i], 10, 20 + i * 20);
    }
    
    // Status
    ctx.fillStyle = isPlaying ? '#00ff00' : '#ff0000';
    ctx.fillText(isPlaying ? '🟢 LIVE 60FPS' : '🔴 PAUSED', width - 120, 20);
    
    if (isDragging) {
      ctx.fillStyle = '#ffff00';
      ctx.font = '16px monospace';
      ctx.fillText('📏 DRAGGING SELECTION', 10, height - 20);
    } else if (isRangeSelectionMode) {
      ctx.fillStyle = '#ffff00';
      ctx.font = '16px monospace';
      ctx.fillText('📏 RANGE SELECT MODE (SHIFT)', 10, height - 20);
    }
    
  }, [selectedPoint, scrubPosition, isPlaying, isDragging, dragStartX, currentDragX, isRangeSelectionMode, getVisibleRange]);
  
  // Draw VDF
  const drawVDF = useCallback(() => {
    const canvas = vdfCanvasRef.current;
    if (!canvas || !selectedPoint) return;
    
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    
    ctx.fillStyle = '#000000';
    ctx.fillRect(0, 0, width, height);
    
    const selectedIndex = Math.floor((selectedPoint.x / canvasWidth) * windowSize);
    const br = dataBuffer.current[selectedIndex * 4] || 0;
    const bt = dataBuffer.current[selectedIndex * 4 + 1] || 0;
    const bn = dataBuffer.current[selectedIndex * 4 + 2] || 0;
    
    const gridSize = 40;
    const cellSize = width / gridSize;
    
    const imageData = ctx.createImageData(width, height);
    const data = imageData.data;
    
    for (let x = 0; x < gridSize; x++) {
      for (let y = 0; y < gridSize; y++) {
        const vx = (x - gridSize/2) * 50;
        const vy = (y - gridSize/2) * 50;
        
        const dist = Math.sqrt(vx*vx + vy*vy);
        const mag_influence = Math.abs(br) * 0.1 + Math.abs(bt) * 0.05 + Math.abs(bn) * 0.03;
        const intensity = Math.exp(-dist/200) * (1 + mag_influence) * (0.8 + 0.4 * Math.sin(Date.now() * 0.001));
        
        const hue = 240 + intensity * 120;
        const sat = 70;
        const light = 30 + intensity * 50;
        
        const rgb = hslToRgb(hue/360, sat/100, light/100);
        
        for (let px = 0; px < cellSize; px++) {
          for (let py = 0; py < cellSize; py++) {
            const pixelX = x * cellSize + px;
            const pixelY = y * cellSize + py;
            if (pixelX < width && pixelY < height) {
              const index = (pixelY * width + pixelX) * 4;
              data[index] = rgb[0];
              data[index + 1] = rgb[1];
              data[index + 2] = rgb[2];
              data[index + 3] = Math.min(255, intensity * 200);
            }
          }
        }
      }
    }
    
    ctx.putImageData(imageData, 0, 0);
    
    ctx.fillStyle = '#ffffff';
    ctx.font = '12px monospace';
    ctx.fillText('Real-time VDF (60fps)', 10, 20);
    ctx.fillText(`Br: ${br.toFixed(1)} nT`, 10, 40);
    ctx.fillText(`|B|: ${Math.sqrt(br*br + bt*bt + bn*bn).toFixed(1)} nT`, 10, 60);
    
  }, [selectedPoint]);
  
  // Animation loop - force frequent redraws
  const animate = useCallback(() => {
    const now = performance.now();
    // Force redraw every frame to ensure changes show up
    drawMainPlot();
    if (showVDF) drawVDF();
    lastDrawTime.current = now;
    animationRef.current = requestAnimationFrame(animate);
  }, [drawMainPlot, drawVDF, showVDF]);
  
  useEffect(() => {
    animationRef.current = requestAnimationFrame(animate);
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [animate]);
  
  // Data updates
  useEffect(() => {
    if (isPlaying) {
      intervalRef.current = setInterval(() => {
        const idx = dataIndex.current % windowSize;
        const t = dataIndex.current * 0.001;
        
        timeBuffer.current[idx] = Date.now();
        dataBuffer.current[idx * 4] = 5 * Math.sin(t) + Math.random() - 0.5;
        dataBuffer.current[idx * 4 + 1] = 3 * Math.cos(t * 1.2) + Math.random() - 0.5;
        dataBuffer.current[idx * 4 + 2] = 2 * Math.sin(t * 0.8) + Math.random() - 0.5;
        dataBuffer.current[idx * 4 + 3] = Math.sqrt(
          Math.pow(dataBuffer.current[idx * 4], 2) + 
          Math.pow(dataBuffer.current[idx * 4 + 1], 2) + 
          Math.pow(dataBuffer.current[idx * 4 + 2], 2)
        );
        
        dataIndex.current++;
        
        if (selectedPoint) {
          const selectedIdx = Math.floor((selectedPoint.x / canvasWidth) * windowSize);
          const bmag = dataBuffer.current[selectedIdx * 4 + 3];
          setAudioFrequency(200 + bmag * 50);
        }
        
      }, 16 / playbackSpeed);
      
      return () => clearInterval(intervalRef.current);
    }
  }, [isPlaying, playbackSpeed, selectedPoint]);
  
  // Mouse handlers
  const handleCanvasMouseDown = useCallback((event) => {
    const canvas = mainCanvasRef.current;
    if (!canvas) return;
    
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const x = (event.clientX - rect.left) * scaleX;
    
    if (isShiftPressed || isRangeSelectionMode) {
      setIsDragging(true);
      setDragStartX(x);
      setCurrentDragX(x);
      event.preventDefault();
    }
  }, [isShiftPressed, isRangeSelectionMode]);
  
  const handleCanvasMouseMove = useCallback((event) => {
    const canvas = mainCanvasRef.current;
    if (!canvas) return;
    
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const x = (event.clientX - rect.left) * scaleX;
    
    if (isDragging) {
      setCurrentDragX(x);
    } else if (!isRangeSelectionMode) {
      setScrubPosition(x);
    }
  }, [isDragging, isRangeSelectionMode]);
  
  const handleCanvasMouseUp = useCallback((event) => {
    if (!isDragging) return;
    
    const canvas = mainCanvasRef.current;
    if (!canvas) return;
    
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const x = (event.clientX - rect.left) * scaleX;
    
    if (dragStartX !== null && Math.abs(x - dragStartX) > 5) {
      const left = Math.min(dragStartX, x);
      const right = Math.max(dragStartX, x);
      
      // Store original range on first zoom
      if (!originalRange) {
        setOriginalRange({ start: 0, end: canvasWidth });
      }
      
      // Convert pixel coordinates to data indices for zoom
      const leftRatio = left / canvasWidth;
      const rightRatio = right / canvasWidth;
      const leftDataIdx = Math.floor(leftRatio * windowSize);
      const rightDataIdx = Math.floor(rightRatio * windowSize);
      
      // Set zoom range using data indices converted back to "normalized" coordinates
      setZoomRange({ 
        start: leftDataIdx, 
        end: rightDataIdx 
      });
      
      // Debug logging
      console.log('Zoom operation:', { 
        dragPixels: { left, right },
        ratios: { leftRatio, rightRatio },
        dataIndices: { leftDataIdx, rightDataIdx },
        windowSize: windowSize
      });
    }
    
    setIsDragging(false);
    setDragStartX(null);
    setCurrentDragX(null);
    setIsRangeSelectionMode(false);
    setIsShiftPressed(false);
    setRangeStartTime(null);
    setRangeEndTime(null);
  }, [isDragging, dragStartX, originalRange]);
  
  const handleCanvasClick = useCallback((event) => {
    if (isDragging) return;
    
    const canvas = mainCanvasRef.current;
    if (!canvas) return;
    
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    const x = (event.clientX - rect.left) * scaleX;
    const y = (event.clientY - rect.top) * scaleY;
    
    if (!isRangeSelectionMode && !isShiftPressed) {
      const visibleRange = getVisibleRange();
      const dataIndex = Math.floor((x / canvasWidth) * visibleRange.count) + visibleRange.start;
      const timestamp = timeBuffer.current[dataIndex];
      
      const br = dataBuffer.current[dataIndex * 4];
      const bt = dataBuffer.current[dataIndex * 4 + 1]; 
      const bn = dataBuffer.current[dataIndex * 4 + 2];
      const bmag = dataBuffer.current[dataIndex * 4 + 3];
      
      // Debug info for clicked point
      console.log('Point clicked:', {
        clickPixelX: x,
        clickRatio: x / canvasWidth,
        visibleRange: visibleRange,
        calculatedDataIndex: dataIndex,
        actualValues: { br, bt, bn, bmag },
        timestamp: new Date(timestamp).toLocaleTimeString()
      });
      
      setSelectedPoint({ x, y, timestamp, dataIndex, br, bt, bn, bmag });
      setShowVDF(true);
    }
  }, [isRangeSelectionMode, isShiftPressed, isDragging, getVisibleRange]);
  
  // Control functions
  const resetZoom = () => {
    setZoomRange(null);
    setOriginalRange(null);
    setRangeStartTime(null);
    setRangeEndTime(null);
    setIsRangeSelectionMode(false);
    setIsShiftPressed(false);
  };
  
  const startAudio = () => {
    if (!selectedPoint) {
      alert('Click on the plot first!');
      return;
    }
    
    setIsAudioPlaying(true);
    setAudioWindow(true);
    
    if (!audioContextRef.current) {
      audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
      gainNodeRef.current = audioContextRef.current.createGain();
      gainNodeRef.current.connect(audioContextRef.current.destination);
      gainNodeRef.current.gain.value = 0.05;
    }
    
    if (audioContextRef.current.state === 'suspended') {
      audioContextRef.current.resume();
    }
    
    if (oscillatorRef.current) oscillatorRef.current.stop();
    
    oscillatorRef.current = audioContextRef.current.createOscillator();
    oscillatorRef.current.frequency.value = audioFrequency;
    oscillatorRef.current.connect(gainNodeRef.current);
    oscillatorRef.current.start();
  };
  
  const stopAudio = () => {
    setIsAudioPlaying(false);
    setAudioWindow(false);
    if (oscillatorRef.current) {
      oscillatorRef.current.stop();
      oscillatorRef.current = null;
    }
  };
  
  // Update oscillator frequency
  useEffect(() => {
    if (oscillatorRef.current && isAudioPlaying) {
      oscillatorRef.current.frequency.setValueAtTime(
        audioFrequency, 
        audioContextRef.current.currentTime
      );
    }
  }, [audioFrequency, isAudioPlaying]);
  
  return (
    <div className="w-full h-screen bg-gray-900 text-white p-4">
      <div className="mb-4">
        <h1 className="text-2xl font-bold mb-2">
          ⚡ OPTIMIZED Real-time Plotbot (60fps Canvas)
        </h1>
        <p className="text-gray-300">
          Canvas-based rendering • 60fps smooth • Drag selection • Zero object allocation
        </p>
      </div>
      
      {/* Controls */}
      <div className="mb-4 bg-gray-800 rounded-lg p-4">
        <div className="flex items-center gap-4">
          <button 
            onClick={() => setIsPlaying(!isPlaying)}
            className={`px-4 py-2 rounded font-semibold transition-colors ${
              isPlaying 
                ? 'bg-red-600 hover:bg-red-700' 
                : 'bg-green-600 hover:bg-green-700'
            }`}
          >
            {isPlaying ? '⏸️ Pause' : '▶️ Play'} Stream
          </button>
          
          <div className="flex items-center gap-2">
            <label className="text-sm">Speed:</label>
            <input 
              type="range" 
              min="0.1" 
              max="5" 
              step="0.1" 
              value={playbackSpeed}
              onChange={(e) => setPlaybackSpeed(parseFloat(e.target.value))}
              className="w-20"
            />
            <span className="text-sm w-12">{playbackSpeed}x</span>
          </div>
          
          <div className="flex items-center gap-2 border-l border-gray-600 pl-4">
            <div className="text-sm text-gray-300">
              <kbd className="px-1 py-0.5 bg-gray-700 rounded text-xs">SHIFT</kbd> + Drag to select • 
              <kbd className="px-1 py-0.5 bg-gray-700 rounded text-xs ml-1">ESC</kbd> Reset Zoom
            </div>
            
            {zoomRange && (
              <button 
                onClick={resetZoom}
                className="px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-sm"
              >
                🔍 Reset Zoom
              </button>
            )}
          </div>
          
          <button 
            onClick={startAudio}
            disabled={!selectedPoint}
            className={`px-3 py-1 rounded text-sm transition-colors ${
              selectedPoint 
                ? 'bg-blue-600 hover:bg-blue-700' 
                : 'bg-gray-600 cursor-not-allowed'
            }`}
          >
            🎵 Audio {selectedPoint ? `(${selectedPoint.bmag?.toFixed(1)} nT)` : ''}
          </button>
          
          {isAudioPlaying && (
            <button 
              onClick={stopAudio}
              className="px-3 py-1 bg-orange-600 hover:bg-orange-700 rounded text-sm"
            >
              🔇 Stop
            </button>
          )}
        </div>
        
        <div className="mt-2 text-sm text-gray-400">
          {isDragging ? (
            "🟡 DRAGGING: Release mouse to zoom to selected range"
          ) : isRangeSelectionMode ? (
            "🟡 SHIFT held • Click and drag to select range"
          ) : zoomRange ? 
            "🔍 Zoomed view • Hold SHIFT + drag for new range • ESC to reset" :
            "Click for points • Hold SHIFT + drag for range zoom • ESC to reset zoom"
          }
          {selectedPoint && (
            <span className="ml-4 text-green-400">
              • Point selected: {selectedPoint.bmag?.toFixed(1)}nT @ {new Date(selectedPoint.timestamp).toLocaleTimeString()}
            </span>
          )}
        </div>
      </div>
      
      <div className="flex gap-4 h-5/6">
        {/* Main canvas plot */}
        <div className="flex-1 bg-gray-800 rounded-lg p-4">
          <h2 className="text-lg font-semibold mb-4">
            PSP Magnetic Field (Canvas 60fps)
            <span className="text-sm text-green-400 ml-2">
              {isPlaying ? '🟢 STREAMING' : '🔴 PAUSED'}
            </span>
          </h2>
          
          <canvas
            ref={mainCanvasRef}
            width={canvasWidth}
            height={canvasHeight}
            className="border border-gray-400 rounded cursor-crosshair block bg-white"
            style={{ 
              width: '100%', 
              height: 'auto',
              maxHeight: '500px',
              imageRendering: 'auto',
              userSelect: 'none',
              backgroundColor: 'white' // Force white background
            }}
            onMouseDown={handleCanvasMouseDown}
            onMouseMove={handleCanvasMouseMove}
            onMouseUp={handleCanvasMouseUp}
            onClick={handleCanvasClick}
          />
          
          <div className="mt-2 text-xs text-gray-400">
            {isDragging ? (
              <span className="text-yellow-400">
                📏 DRAGGING SELECTION: Release mouse to complete zoom
              </span>
            ) : isRangeSelectionMode ? (
              <span className="text-yellow-400">
                📏 SHIFT HELD: Click and drag to select range • Release SHIFT to cancel
              </span>
            ) : zoomRange ? (
              <span className="text-cyan-400">
                🔍 ZOOMED: Showing selected range • Hold SHIFT + drag for new range • ESC to reset
              </span>
            ) : (
              "Click for point selection • Hold SHIFT + click and drag for range zoom • ESC resets zoom"
            )}
          </div>
        </div>
        
        {/* VDF panel */}
        {showVDF && (
          <div className="w-96 bg-gray-800 rounded-lg p-4">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">60fps VDF</h3>
              <button 
                onClick={() => setShowVDF(false)}
                className="text-gray-400 hover:text-white text-xl"
              >
                ×
              </button>
            </div>
            
            <canvas
              ref={vdfCanvasRef}
              width={300}
              height={300}
              className="border border-gray-600 rounded"
            />
            
            <div className="mt-4 p-3 bg-gray-700 rounded text-sm">
              <div>Freq: {audioFrequency.toFixed(1)} Hz</div>
              <div>Selected: {selectedPoint ? 
                new Date(selectedPoint.timestamp).toLocaleTimeString() : 'None'
              }</div>
            </div>
          </div>
        )}
      </div>
      
      {/* Audio window */}
      {audioWindow && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-6 w-2/3 h-2/3">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold">🎵 Audio Visualization</h2>
              <button 
                onClick={() => setAudioWindow(false)}
                className="text-gray-400 hover:text-white text-2xl"
              >
                ×
              </button>
            </div>
            
            <div className="text-center p-8">
              <div className="text-6xl mb-4">🎵</div>
              <div className="text-xl">Audio playing at {audioFrequency.toFixed(1)} Hz</div>
              <div className="text-gray-400 mt-2">
                Real spectrogram would go here (also canvas-based for 60fps)
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default OptimizedRealTimePlotbot;