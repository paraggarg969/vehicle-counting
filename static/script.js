const video = document.getElementById('video');
const videoUpload = document.getElementById('video-upload');
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
const drawBtn = document.getElementById('draw-btn');
const stopBtn = document.getElementById('stop-btn');
const eraseLastBtn = document.getElementById('erase-last-btn');
const eraseAllBtn = document.getElementById('erase-all-btn');
// const setline = document.getElementById('start')

let isDrawing = false;
var lines = [];
var tempLine = [];

videoUpload.addEventListener('change', handleVideoUpload);
canvas.addEventListener('mousedown', startDrawing);
canvas.addEventListener('mousemove', draw);
canvas.addEventListener('mouseup', stopDrawing);
drawBtn.addEventListener('click', toggleDrawing);
// eraseLastBtn.addEventListener('click', eraseLastLine);
eraseAllBtn.addEventListener('click', eraseAllLines);
// setline.addEventListener('click', updateLineCoordinates);

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

function handleVideoUpload(event) {
    const file = event.target.files[0];

    if (!file) {
        console.error('No file selected');
        return;
    }

    // const url = URL.createObjectURL(file);
    // video.src = url;
    // video.play();

    const formData = new FormData();
    formData.append('video', file);

    fetch('/upload-video', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // video.src = URL.createObjectURL(file); // Show the video
            video.src = data.video_url;
            video.play();
        } else {
            console.error('Upload failed:', data.message);
        }
    })
    .catch(error => console.error('Error:', error.message));
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
            updateLineCoordinates();
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
        // updateLineCoordinates();
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

function updateLineCoordinates() {
    console.log("update Line Coordinates called");
    console.log("Lines array:", tempLine); 
    if (tempLine.length > 0) {
        fetch('/set-line', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ x1: tempLine[0], y1: tempLine[1], x2: tempLine[2], y2: tempLine[3] }),
        })
        .then(response => response.json())
        .then(data => {
            console.log(data.message)
            console.log('Processing started');
            // video.src = '/video-feed';
            // video.play();
            // refreshVideoFeed();
        })
        .catch(error => console.error('Error:', error));
    }
}

    // function refreshVideoFeed() {
    //     const video = document.getElementById('video');

    //     // Set the video source to the video feed endpoint
    //     // video.src = '/video-feed?' + new Date().getTime();  // Add a timestamp to force reload
    //     video.src = '/video-feed';  // Add a timestamp to force reload
    //     video.play();  // Ensure video starts playing
    //     console.log("s1");
    // }

// function eraseLastLine() {
//     if (lines.length > 0) {
//         lines.pop(); 
//         ctx.clearRect(0, 0, canvas.width, canvas.height); 
//         redrawLines(); 
//     }
// }

function eraseAllLines() {
    lines = []; 
    ctx.clearRect(0, 0, canvas.width, canvas.height); 
}