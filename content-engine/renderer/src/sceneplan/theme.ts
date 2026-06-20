import type {GlowMode} from './types';

/**
 * Maps theme.glow_mode to a CSS text-shadow/filter glow recipe. Pure
 * presentation — no decision logic about *when* to glow, that's encoded by
 * the Brain in theme.glow_mode already.
 */
export function glowTextShadow(color: string, mode: GlowMode): string {
  switch (mode) {
    case 'full':
      return `0 0 6px ${color}, 0 0 18px ${color}, 0 0 36px ${color}`;
    case 'subtle':
      return `0 0 4px ${color}, 0 0 10px ${color}`;
    case 'reduced':
      return `0 0 3px ${color}`;
    case 'minimal':
    default:
      return 'none';
  }
}

export function glowBoxShadow(color: string, mode: GlowMode): string {
  switch (mode) {
    case 'full':
      return `0 0 10px ${color}, 0 0 24px ${color}`;
    case 'subtle':
      return `0 0 6px ${color}`;
    case 'reduced':
      return `0 0 3px ${color}`;
    case 'minimal':
    default:
      return 'none';
  }
}

export function pickColor(
  colors: Record<string, string> | undefined,
  key: string,
  fallback: string,
): string {
  if (!colors) return fallback;
  return colors[key] ?? fallback;
}
