# ScenePlan — Brain → Renderer Contract

`ScenePlan` ist das einzige Interface zwischen der Python-"Brain" (Datenlogik, Kamera,
Events, Timing, QA) und dem Remotion-"Renderer" (reines Pixel-Malen). Der Renderer
liest ausschließlich diese JSON-Struktur, importiert nie Brain-Code und enthält keine
Geschäftslogik.

`schema_version: 1`

```jsonc
{
  "schema_version": 1,
  "video_id": "string",
  "topic": {
    "assets": ["BTC-USD", "^GSPC", "GC=F"],
    "period_days": 1825,
    "locale": "de"
  },
  "fps": 30,
  "duration": {
    "total_frames": 600,
    "total_duration_sec": 20.0,
    "phases": {
      "intro": { "start_frame": 0, "end_frame": 30 },
      "race": { "start_frame": 30, "end_frame": 480 },
      "final_hold": { "start_frame": 480, "end_frame": 540 },
      "endscreen": { "start_frame": 540, "end_frame": 600 }
    }
  },
  "data_series": [
    {
      "ticker": "BTC-USD",
      "label": "Bitcoin",
      "color": "#F7931A",
      "dates": ["2021-01-01", "..."],
      "values": [1000.0, 1020.5, "..."]
    }
  ],
  "camera": {
    "policy": "stock_value | percent | high_volatility",
    "keyframes": [
      { "frame": 0, "x_min": 0, "x_max": 30, "y_min": 0, "y_max": 1200 }
    ]
  },
  "time_map": {
    "enabled": true,
    "control_points": [{ "frame": 30, "data_index": 0.0 }]
  },
  "events": [
    {
      "frame_start": 120,
      "frame_end": 180,
      "ticker": "BTC-USD",
      "type": "crash | ath_record | geopolitical_risk | energy_shock | financial_crisis | macro_rate | earnings | default",
      "label": "string (<=42 chars)",
      "style_ref": "string (key into theme.event_styles)"
    }
  ],
  "theme": {
    "id": "string",
    "colors": { "bg": {}, "text": {}, "accent": {} },
    "font_family": "string",
    "glow_mode": "full | subtle | reduced | minimal",
    "event_styles": { "crash": { "color": "#...", "pulse": true } }
  },
  "hook_variant": { "id": "string" },
  "endscreen": {
    "final_values": [{ "ticker": "BTC-USD", "value": 5400.0, "gain_pct": 440.0 }],
    "thumbnail_source_frame": 540
  },
  "qa": {
    "hard_fail": false,
    "results": [{ "check": "string", "passed": true, "detail": "string" }]
  }
}
```

## Invarianten

- Frames sind die einzige Zeiteinheit, die der Renderer kennt — keine Sekunden-Umrechnung im Renderer.
- `camera.keyframes` sind absolute Achsen-Grenzen pro Frame-Stützpunkt; der Renderer interpoliert zwischen ihnen mit Remotion `interpolate`/`spring`, rechnet sie nicht neu aus.
- `events` dürfen sich nicht mit `final_hold`/`endscreen`-Phasen überlappen (von der Brain-QA hart geprüft, siehe `EventQA`).
- `qa.hard_fail = true` bedeutet: Renderer darf trotzdem rendern (für Debug-Zwecke), aber `distribution` darf das Ergebnis nicht automatisch posten.
