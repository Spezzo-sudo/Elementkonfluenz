import React from 'react';
import {useCurrentFrame} from 'remotion';
import type {ScenePlan} from '../sceneplan/types';
import {eventOpacity} from '../sceneplan/interpolation';
import {glowTextShadow} from '../sceneplan/theme';

interface EventOverlayProps {
  scenePlan: ScenePlan;
}

/**
 * Renders all `events` whose [frame_start, frame_end] window currently has
 * non-zero opacity. Opacity is computed via `eventOpacity()`, a continuous
 * `interpolate()`-based fade in/hold/fade out — never a boolean
 * "frame is inside window" snap — so events visually ease in and out.
 */
export const EventOverlay: React.FC<EventOverlayProps> = ({scenePlan}) => {
  const frame = useCurrentFrame();
  const {events, theme} = scenePlan;

  return (
    <div style={{position: 'absolute', inset: 0, pointerEvents: 'none'}}>
      {events.map((event, idx) => {
        const opacity = eventOpacity(frame, event.frame_start, event.frame_end);
        if (opacity <= 0.001) {
          return null;
        }

        const style = theme.event_styles[event.style_ref] ?? {
          color: theme.colors.accent.primary ?? '#ffffff',
          pulse: false,
        };

        // Pulse is a purely cosmetic, continuous oscillation — still a
        // function of `frame`, not a discrete on/off toggle.
        const pulseScale = style.pulse
          ? 1 + 0.04 * Math.sin((frame / 6) * Math.PI)
          : 1;

        return (
          <div
            key={`${event.ticker}-${event.frame_start}-${idx}`}
            style={{
              position: 'absolute',
              top: '8%',
              left: '50%',
              transform: `translateX(-50%) scale(${pulseScale})`,
              opacity,
              backgroundColor: 'rgba(0,0,0,0.55)',
              border: `2px solid ${style.color}`,
              borderRadius: 10,
              padding: '10px 22px',
              color: style.color,
              fontFamily: theme.font_family,
              fontWeight: 700,
              fontSize: 28,
              textShadow: glowTextShadow(style.color, theme.glow_mode),
              whiteSpace: 'nowrap',
            }}
          >
            {event.ticker}: {event.label}
          </div>
        );
      })}
    </div>
  );
};
