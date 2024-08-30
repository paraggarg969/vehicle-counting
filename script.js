const video = document.getElementById('video');
const videoUpload = document.getElementById('video-upload');
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
const drawBtn = document.getElementById('draw-btn');
const stopBtn = document.getElementById('stop-btn');

let isDrawing = false;
let lines = [];
let tempLine = [];

videoUpload.addEventListener('change', handleVideoUpload);
canvas.addEventListener('mousedown', startDrawing);
canvas.addEventListener('mousemove', draw);
canvas.addEventListener('mouseup', stopDrawing);
drawBtn.addEventListener('click', toggleDrawing);
stopBtn.addEventListener('click', stopDrawing);

function handleVideoUpload(event) {
    const file = event.target.files[0];
    const url = URL.createObjectURL(file);
    video.src = url;
    video.play();
}

function toggleDrawing() {
    isDrawing = !isDrawing;
    if (isDrawing) {
        drawBtn.textContent = 'Drawing... Click to Erase Last Line';
    } else {
        drawBtn.textContent = 'Draw Line';
        if (tempLine.length === 4) {
            lines.push(tempLine);
            console.log(`Line coordinates: (${tempLine[0]}, ${tempLine[1]}) to (${tempLine[2]}, ${tempLine[3]})`);
            tempLine = [];
        }
    }
}

function startDrawing(event) {
    if (isDrawing) {
        const rect = canvas.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;

        if (tempLine.length === 2) {
            tempLine.push(x, y);
            ctx.lineTo(x, y);
            ctx.stroke();
            stopDrawing();
        } else {
            ctx.beginPath();
            ctx.moveTo(x, y);
            tempLine = [x, y];
        }
    }
}

function draw(event) {
    if (!isDrawing || tempLine.length !== 2) return;

    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    redrawLines();

    ctx.beginPath();
    ctx.moveTo(tempLine[0], tempLine[1]);
    ctx.lineTo(x, y);
    ctx.stroke();
}

function stopDrawing() {
    if (!isDrawing && tempLine.length === 4) {
        tempLine = [];
    }
}

function redrawLines() {
    lines.forEach(line => {
        ctx.beginPath();
        ctx.moveTo(line[0], line[1]);
        ctx.lineTo(line[2], line[3]);
        ctx.stroke();
    });
}