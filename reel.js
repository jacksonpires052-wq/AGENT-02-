// Agente 02 - monta o Reels (MP4 vertical) a partir dos quadros, com ffmpeg
const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');

function montarReel(quadros, saida, trilha, duracao = 10) {
  const FPS = 30, SEG = duracao / quadros.length, d = Math.round(SEG * FPS);
  const args = ['-y', '-loglevel', 'error'];
  quadros.forEach(q => args.push('-i', q));
  const temSom = trilha && fs.existsSync(trilha);
  if (temSom) args.push('-stream_loop', '-1', '-i', trilha);
  else args.push('-f', 'lavfi', '-i', 'anullsrc=channel_layout=stereo:sample_rate=44100');
  const total = SEG * quadros.length;
  const f = quadros.map((_, i) =>
    `[${i}:v]scale=2160:3840,zoompan=z='min(zoom+0.0015,1.08)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=${d}:s=1080x1920:fps=${FPS},setsar=1[v${i}]`);
  f.push(quadros.map((_, i) => `[v${i}]`).join('') + `concat=n=${quadros.length}:v=1:a=0,format=yuv420p[v]`);
  const ai = quadros.length;
  f.push(`[${ai}:a]atrim=0:${total},afade=t=out:st=${total - 1}:d=1,asetpts=PTS-STARTPTS[a]`);
  args.push('-filter_complex', f.join(';'), '-map', '[v]', '-map', '[a]',
    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '23', '-r', String(FPS), '-pix_fmt', 'yuv420p',
    '-c:a', 'aac', '-b:a', '128k', '-t', String(total), '-movflags', '+faststart', saida);
  execFileSync('ffmpeg', args, { stdio: 'inherit' });
  return saida;
}

module.exports = { montarReel };
