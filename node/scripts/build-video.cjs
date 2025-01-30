// node/scripts/build-video.cjs
const { execSync } = require("child_process");
const path = require("path");

try {
  const framesPattern = path.join("frames", "frame_%05d.png");
  const audioFile = "audio.wav";
  const outputFile = path.join("output", "video.mp4");

  const cmd = `ffmpeg -framerate 30 -i ${framesPattern} -i ${audioFile} -c:v libx264 -c:a aac -pix_fmt yuv420p -shortest ${outputFile}`;

  console.log("Running FFmpeg command:", cmd);
  execSync(cmd, { stdio: "inherit" });

  console.log("Video generation succeeded!");
} catch (error) {
  console.error("Video generation failed:", error);
  process.exit(1);
}