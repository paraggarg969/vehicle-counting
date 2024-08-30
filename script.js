const video = document.getElementById('video');
const videoUpload = document.getElementById('video-upload');
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
const drawBtn = document.getElementById('draw-btn');
const stopBtn = document.getElementById('stop-btn');
const eraseLastBtn = document.getElementById('erase-last-btn');
const eraseAllBtn = document.getElementById('erase-all-btn');

let isDrawing = false;
let lines = [];
let tempLine = [];

videoUpload.addEventListener('change', handleVideoUpload);
canvas.addEventListener('mousedown', startDrawing);
canvas.addEventListener('mousemove', draw);
canvas.addEventListener('mouseup', stopDrawing);
drawBtn.addEventListener('click', toggleDrawing);
// stopBtn.addEventListener('click', stopDrawing);
// eraseLastBtn.addEventListener('click', eraseLastLine);
eraseAllBtn.addEventListener('click', eraseAllLines);

var orgwidth = 0;
var orgheight = 0;
let videoScaleFactorWidth = 1;
let videoScaleFactorHeight = 1;

video.onplaying = function () {
    orgwidth = video.videoWidth;
    orgheight = video.videoHeight;
    console.log("video dimens loaded w="+orgwidth+" h="+orgheight);

    videoScaleFactorWidth = orgwidth / video.clientWidth;
    videoScaleFactorHeight = orgheight / video.clientHeight;
    console.log("client video dimens loaded w="+video.clientWidth+" h="+video.clientHeight);
    console.log("Scale video dimens loaded w="+videoScaleFactorWidth+" h="+videoScaleFactorHeight);
}

// video.addEventListener('loadedmetadata', () => {
//     // Update canvas size to match the video's display size
//     canvas.width = video.videoWidth;
//     canvas.height = video.videoHeight;
//     console.log("video dimens loaded w="+canvas.width+" h="+canvas.height);
// });

function handleVideoUpload(event) {
    const file = event.target.files[0];
    const url = URL.createObjectURL(file);
    video.src = url;
    video.play();
}

function toggleDrawing() {
    isDrawing = !isDrawing;
    if (isDrawing) {
        drawBtn.textContent = 'Drawing... Click to Stop';
    } else {
        drawBtn.textContent = 'Draw Line';
        if (tempLine.length === 4) {
            lines.push(tempLine);
            logLineCoordinates();
            tempLine = [];
        }
    }
}

function startDrawing(event) {
    if (isDrawing) {
        const rect = canvas.getBoundingClientRect();
        const x = (event.clientX - rect.left) * videoScaleFactorWidth;
        const y = (event.clientY - rect.top) * videoScaleFactorHeight;

        if (tempLine.length === 2) {
            tempLine.push(x, y);
            ctx.lineTo(x / videoScaleFactorWidth, y / videoScaleFactorHeight);
            ctx.stroke();
            logLineCoordinates();
        } else {
            ctx.beginPath();
            ctx.moveTo(x / videoScaleFactorWidth, y / videoScaleFactorHeight);
            tempLine = [x, y];
        }
    }
}

function draw(event) {
    if (!isDrawing || tempLine.length !== 2) return;

    const rect = canvas.getBoundingClientRect();
    const x = (event.clientX - rect.left) * videoScaleFactorWidth;
    const y = (event.clientY - rect.top) * videoScaleFactorHeight;

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    redrawLines();

    ctx.beginPath();
    ctx.moveTo(tempLine[0] / videoScaleFactorWidth, tempLine[1] / videoScaleFactorHeight);
    ctx.lineTo(x / videoScaleFactorWidth, y / videoScaleFactorHeight);
    ctx.strokeStyle = 'red'; 
    ctx.lineWidth = 2; 
    ctx.stroke();
}

function stopDrawing() {
    if (isDrawing && tempLine.length === 4) {
        tempLine = [];
    }
}

function redrawLines() {
    lines.forEach(line => {
        ctx.beginPath();
        ctx.moveTo(line[0] / videoScaleFactorWidth, line[1] / videoScaleFactorHeight);
        ctx.lineTo(line[2] / videoScaleFactorWidth, line[3] / videoScaleFactorHeight);
        ctx.strokeStyle = 'red'; 
        ctx.lineWidth = 2; 
        ctx.stroke();
    });
}

function logLineCoordinates() {
    if (tempLine.length === 4) {
        const [x1, y1, x2, y2] = tempLine;
        let direction = 'Line';
        if (x1 === x2) {
            direction = y2 > y1 ? 'Down' : 'Up';
        } else if (y1 === y2) {
            direction = x2 > x1 ? 'Right' : 'Left';
        }
        console.log(`${direction} coordinates: (${x1}, ${y1}) to (${x2}, ${y2})`);
    }
}

function eraseLastLine() {
    if (lines.length > 0) {
        lines.pop(); 
        ctx.clearRect(0, 0, canvas.width, canvas.height); 
        redrawLines(); 
    }
}

function eraseAllLines() {
    lines = []; 
    ctx.clearRect(0, 0, canvas.width, canvas.height); 
}