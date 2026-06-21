import React from 'react';
import {interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import type {EmpireScenePlan} from '../../sceneplan/empireTypes';

interface RegisterCardsPhaseProps {
  scenePlan: EmpireScenePlan;
}

const COLUMNS = 2;
const COLUMN_GAP = 24;
const ROW_GAP = 16;
const SIDE_MARGIN = 56;
const TOP_AREA = 220;
const BOTTOM_MARGIN = 80;
const MIN_CARD_HEIGHT = 90;
const MAX_CARD_HEIGHT = 220;

/**
 * Brand "card wall" — each card cascades in (fade + slide-up), staggered by
 * index, all driven by interpolate() so the stagger reads as one continuous
 * cascade rather than discrete pop-ins. Card background uses the brand's
 * own color (BrandCard.color/text_color), the per-brand visual identity the
 * Brain already curated — the renderer never invents brand colors.
 */
export const RegisterCardsPhase: React.FC<RegisterCardsPhaseProps> = ({
  scenePlan,
}) => {
  const frame = useCurrentFrame();
  const {width} = useVideoConfig();
  const {brands, theme, owner, duration} = scenePlan;
  const phase = duration.phases.register_cards;
  const phaseFrame = frame - phase.start_frame;
  const phaseLen = Math.max(1, phase.end_frame - phase.start_frame);

  const rows = Math.ceil(brands.length / COLUMNS);
  const availableWidth = width - 2 * SIDE_MARGIN - (COLUMNS - 1) * COLUMN_GAP;
  const cardWidth = availableWidth / COLUMNS;
  const availableHeight = 1920 - TOP_AREA - BOTTOM_MARGIN - (rows - 1) * ROW_GAP;
  const cardHeight = Math.max(
    MIN_CARD_HEIGHT,
    Math.min(MAX_CARD_HEIGHT, availableHeight / Math.max(rows, 1)),
  );

  const staggerWindow = phaseLen * 0.6;
  const staggerStep = staggerWindow / Math.max(brands.length, 1);

  return (
    <div style={{position: 'absolute', inset: 0}}>
      <div
        style={{
          position: 'absolute',
          top: 64,
          left: 0,
          right: 0,
          textAlign: 'center',
          color: '#ffffff',
          fontSize: 30,
          fontWeight: 800,
          letterSpacing: 3,
          opacity: 0.85,
        }}
      >
        REGISTER · {owner.display_name.toUpperCase()}
      </div>

      {brands.map((brand, i) => {
        const col = i % COLUMNS;
        const row = Math.floor(i / COLUMNS);
        const left = SIDE_MARGIN + col * (cardWidth + COLUMN_GAP);
        const top = TOP_AREA + row * (cardHeight + ROW_GAP);

        const appearStart = i * staggerStep;
        const appearEnd = appearStart + 14;
        const opacity = interpolate(
          phaseFrame,
          [appearStart, appearEnd],
          [0, 1],
          {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'},
        );
        const slideY = interpolate(
          phaseFrame,
          [appearStart, appearEnd],
          [28, 0],
          {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'},
        );

        return (
          <div
            key={brand.name}
            style={{
              position: 'absolute',
              left,
              top,
              width: cardWidth,
              height: cardHeight,
              opacity,
              transform: `translateY(${slideY}px)`,
              backgroundColor: brand.color,
              borderRadius: 10,
              boxShadow: '0 8px 24px rgba(0,0,0,0.45)',
              overflow: 'hidden',
            }}
          >
            <div
              style={{
                position: 'absolute',
                left: 0,
                top: 0,
                bottom: 0,
                width: 5,
                backgroundColor: theme.accent_color,
                opacity: 0.7,
              }}
            />
            <div
              style={{
                position: 'absolute',
                inset: 0,
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                paddingLeft: 22,
                paddingRight: 16,
              }}
            >
              <div
                style={{
                  color: brand.text_color,
                  fontSize: Math.min(28, cardHeight * 0.3),
                  fontWeight: 800,
                  lineHeight: 1.1,
                  whiteSpace: 'nowrap',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                }}
              >
                {brand.name}
              </div>
              <div
                style={{
                  color: brand.text_color,
                  opacity: 0.85,
                  fontSize: Math.min(16, cardHeight * 0.18),
                  fontWeight: 600,
                  marginTop: 4,
                }}
              >
                {brand.category} · seit {brand.year}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};
