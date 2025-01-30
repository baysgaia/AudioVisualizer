// node/scripts/build-video.js
const { execSync } = require("child_process");

try {
  // frames/frame_%05d.png と audio.wav が存在し、output ディレクトリも作成済み想定
  execSync(
    'ffmpeg -framerate 30 -i frames/frame_%05d.png -i audio.wav -c:v libx264 -c:a aac -pix_fmt yuv420p output/video.mp4',
    { stdio: 'inherit' }
  );
  console.log('Video generation succeeded!');
} catch (error) {
  console.error('Video generation failed:', error);
  process.exit(1);
}