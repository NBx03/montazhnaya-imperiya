import os

def main():
    icons_dir = os.path.join(os.path.dirname(__file__), 'public', 'icons')
    images_dir = os.path.join(os.path.dirname(__file__), 'public', 'images')
    os.makedirs(icons_dir, exist_ok=True)
    os.makedirs(images_dir, exist_ok=True)

    brands = {
        'hikvision.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 50" fill="none">
            <text x="10" y="34" font-family="'JetBrains Mono', monospace" font-size="22" font-weight="800" fill="#FFFFFF" letter-spacing="2">HIKVISION</text>
            <circle cx="180" cy="27" r="4" fill="#E02D37" />
        </svg>''',
        'dahua.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 180 50" fill="none">
            <text x="10" y="34" font-family="'JetBrains Mono', monospace" font-size="22" font-weight="800" fill="#FFFFFF" letter-spacing="3">alhua</text>
            <rect x="150" y="18" width="12" height="12" fill="#E02D37" rx="2"/>
        </svg>''',
        'sigur.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 160 50" fill="none">
            <text x="10" y="34" font-family="'JetBrains Mono', monospace" font-size="24" font-weight="800" fill="#FFFFFF" letter-spacing="2">SIGUR</text>
            <path d="M135 16 L145 26 L135 36" stroke="#E02D37" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>''',
        'bolid.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 170 50" fill="none">
            <rect x="10" y="14" width="24" height="24" rx="4" fill="#E02D37"/>
            <path d="M16 26 L22 20 L28 26 L22 32 Z" fill="#FFFFFF"/>
            <text x="44" y="34" font-family="'JetBrains Mono', monospace" font-size="22" font-weight="800" fill="#FFFFFF" letter-spacing="2">БОЛИД</text>
        </svg>''',
        'rubezh.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 170 50" fill="none">
            <text x="10" y="34" font-family="'JetBrains Mono', monospace" font-size="22" font-weight="800" fill="#FFFFFF" letter-spacing="2">РУБЕЖ</text>
            <line x1="125" y1="27" x2="150" y2="27" stroke="#E02D37" stroke-width="3" stroke-linecap="round"/>
        </svg>''',
        'trassir.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 180 50" fill="none">
            <text x="10" y="34" font-family="'JetBrains Mono', monospace" font-size="22" font-weight="800" fill="#FFFFFF" letter-spacing="2">TRASSIR</text>
            <circle cx="160" cy="20" r="4" fill="#E02D37"/>
        </svg>''',
        'parsec.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 170 50" fill="none">
            <text x="10" y="34" font-family="'JetBrains Mono', monospace" font-size="22" font-weight="800" fill="#FFFFFF" letter-spacing="2">PARSEC</text>
            <rect x="145" y="19" width="10" height="14" rx="2" stroke="#E02D37" stroke-width="2"/>
        </svg>''',
        'dkc.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 150 50" fill="none">
            <text x="10" y="35" font-family="'JetBrains Mono', monospace" font-size="26" font-weight="900" fill="#FFFFFF" letter-spacing="4">DKC</text>
            <circle cx="115" cy="26" r="5" stroke="#E02D37" stroke-width="3"/>
        </svg>''',
        'legrand.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 180 50" fill="none">
            <text x="10" y="34" font-family="'JetBrains Mono', monospace" font-size="22" font-weight="800" fill="#FFFFFF" letter-spacing="2">legrand</text>
            <rect x="145" y="21" width="14" height="10" fill="#E02D37"/>
        </svg>''',
        'suprema.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 190 50" fill="none">
            <text x="10" y="34" font-family="'JetBrains Mono', monospace" font-size="22" font-weight="800" fill="#FFFFFF" letter-spacing="2">suprema</text>
            <polygon points="165,19 173,31 157,31" fill="#E02D37"/>
        </svg>'''
    }

    for fname, svg in brands.items():
        with open(os.path.join(icons_dir, fname), 'w', encoding='utf-8') as f:
            f.write(svg.strip())

    # Create SVG illustrations for cards
    cards = {
        'service-cctv.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 400" fill="none">
            <rect width="600" height="400" fill="#12151B"/>
            <defs>
                <radialGradient id="cctv-glow" cx="50%" cy="50%" r="50%">
                    <stop offset="0%" stop-color="#E02D37" stop-opacity="0.25"/>
                    <stop offset="100%" stop-color="#12151B" stop-opacity="0"/>
                </radialGradient>
            </defs>
            <circle cx="300" cy="200" r="160" fill="url(#cctv-glow)"/>
            <!-- Grid lines -->
            <path d="M50 200 H550 M300 50 V350" stroke="#FFFFFF" stroke-opacity="0.05" stroke-dasharray="4 4"/>
            <circle cx="300" cy="200" r="120" stroke="#FFFFFF" stroke-opacity="0.1" stroke-width="1"/>
            <circle cx="300" cy="200" r="80" stroke="#E02D37" stroke-opacity="0.3" stroke-width="1.5" stroke-dasharray="6 6"/>
            <!-- Camera body -->
            <path d="M220 180 L290 140 L350 140 L380 180 L350 240 L270 240 Z" fill="#1B1F27" stroke="#FFFFFF" stroke-opacity="0.2" stroke-width="2"/>
            <circle cx="350" cy="200" r="24" fill="#0E1014" stroke="#E02D37" stroke-width="3"/>
            <circle cx="350" cy="200" r="10" fill="#E02D37"/>
            <circle cx="353" cy="197" r="3" fill="#FFFFFF"/>
            <!-- Bracket & wire -->
            <path d="M220 180 L180 180 L160 210" stroke="#5A6275" stroke-width="6" stroke-linecap="round"/>
            <rect x="150" y="195" width="16" height="40" rx="3" fill="#2A303D"/>
            <!-- Rec HUD -->
            <rect x="70" y="60" width="100" height="26" rx="4" fill="#0E1014" fill-opacity="0.8" stroke="#E02D37" stroke-width="1"/>
            <circle cx="85" cy="73" r="4" fill="#E02D37"/>
            <text x="96" y="77" font-family="'JetBrains Mono', monospace" font-size="11" font-weight="700" fill="#FFFFFF">LIVE 4K</text>
            <text x="470" y="77" font-family="'JetBrains Mono', monospace" font-size="12" fill="#8E95A5">CAM 01/32</text>
            <!-- Crosshairs -->
            <path d="M290 200 H310 M300 190 V210" stroke="#E02D37" stroke-width="2"/>
        </svg>''',
        'service-skud.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 400" fill="none">
            <rect width="600" height="400" fill="#12151B"/>
            <defs>
                <radialGradient id="skud-glow" cx="50%" cy="50%" r="50%">
                    <stop offset="0%" stop-color="#E02D37" stop-opacity="0.2"/>
                    <stop offset="100%" stop-color="#12151B" stop-opacity="0"/>
                </radialGradient>
            </defs>
            <circle cx="300" cy="200" r="150" fill="url(#skud-glow)"/>
            <!-- Turnstile / barrier gate silhouette -->
            <rect x="180" y="140" width="45" height="180" rx="6" fill="#1C212B" stroke="#FFFFFF" stroke-opacity="0.15" stroke-width="2"/>
            <rect x="375" y="140" width="45" height="180" rx="6" fill="#1C212B" stroke="#FFFFFF" stroke-opacity="0.15" stroke-width="2"/>
            <!-- Turnstile rotor blades -->
            <line x1="225" y1="200" x2="300" y2="180" stroke="#FFFFFF" stroke-opacity="0.4" stroke-width="8" stroke-linecap="round"/>
            <line x1="300" y1="180" x2="375" y2="200" stroke="#FFFFFF" stroke-opacity="0.4" stroke-width="8" stroke-linecap="round"/>
            <!-- Biometric reader / screen -->
            <rect x="186" y="155" width="33" height="50" rx="4" fill="#0E1014" stroke="#E02D37" stroke-width="1.5"/>
            <!-- Access Granted icon -->
            <circle cx="202" cy="180" r="10" fill="#E02D37" fill-opacity="0.2"/>
            <path d="M197 180 L200 183 L208 175" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <!-- Status badges -->
            <rect x="230" y="90" width="140" height="30" rx="4" fill="#0E1014" fill-opacity="0.8" stroke="rgba(255,255,255,0.1)" stroke-width="1"/>
            <text x="245" y="110" font-family="'JetBrains Mono', monospace" font-size="11" font-weight="700" fill="#E02D37">ACCESS: RFID / FACE</text>
        </svg>''',
        'service-alarm.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 400" fill="none">
            <rect width="600" height="400" fill="#12151B"/>
            <circle cx="300" cy="200" r="130" stroke="#E02D37" stroke-opacity="0.15" stroke-width="2" stroke-dasharray="8 8"/>
            <circle cx="300" cy="200" r="90" stroke="#E02D37" stroke-opacity="0.3" stroke-width="2"/>
            <!-- Motion sensor shape -->
            <rect x="250" y="130" width="100" height="140" rx="16" fill="#1B1F27" stroke="#FFFFFF" stroke-opacity="0.2" stroke-width="2"/>
            <!-- Fresnel Lens -->
            <path d="M265 170 Q300 200 335 170 Q300 220 265 170 Z" fill="#252B37" stroke="#FFFFFF" stroke-opacity="0.3" stroke-width="1.5"/>
            <!-- LED indicator -->
            <circle cx="300" cy="150" r="4" fill="#E02D37"/>
            <circle cx="300" cy="150" r="8" fill="#E02D37" fill-opacity="0.3"/>
            <!-- Alarm radio wave pulses -->
            <path d="M370 170 A 50 50 0 0 1 370 230" stroke="#E02D37" stroke-width="2.5" stroke-linecap="round"/>
            <path d="M390 155 A 80 80 0 0 1 390 245" stroke="#E02D37" stroke-width="2" stroke-linecap="round" stroke-opacity="0.6"/>
            <path d="M230 170 A 50 50 0 0 0 230 230" stroke="#E02D37" stroke-width="2.5" stroke-linecap="round"/>
            <path d="M210 155 A 80 80 0 0 0 210 245" stroke="#E02D37" stroke-width="2" stroke-linecap="round" stroke-opacity="0.6"/>
            <!-- Badge -->
            <text x="300" y="320" text-anchor="middle" font-family="'JetBrains Mono', monospace" font-size="12" fill="#8E95A5" letter-spacing="2">PIR MOTION &amp; PERIMETER</text>
        </svg>''',
        'service-fire.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 400" fill="none">
            <rect width="600" height="400" fill="#12151B"/>
            <defs>
                <radialGradient id="fire-glow" cx="50%" cy="45%" r="45%">
                    <stop offset="0%" stop-color="#E02D37" stop-opacity="0.3"/>
                    <stop offset="100%" stop-color="#12151B" stop-opacity="0"/>
                </radialGradient>
            </defs>
            <circle cx="300" cy="190" r="140" fill="url(#fire-glow)"/>
            <!-- Optical smoke detector ceiling mount -->
            <ellipse cx="300" cy="190" rx="110" ry="110" fill="#1A1E26" stroke="#FFFFFF" stroke-opacity="0.15" stroke-width="2"/>
            <ellipse cx="300" cy="190" rx="80" ry="80" fill="#202530" stroke="#E02D37" stroke-opacity="0.4" stroke-width="2"/>
            <!-- Sensor chamber vents -->
            <circle cx="300" cy="190" r="45" fill="#12151B" stroke="#FFFFFF" stroke-opacity="0.2" stroke-width="1.5"/>
            <!-- Smoke vent slots -->
            <circle cx="300" cy="190" r="58" stroke="#FFFFFF" stroke-opacity="0.1" stroke-width="6" stroke-dasharray="10 8"/>
            <!-- Red beacon LED -->
            <circle cx="300" cy="190" r="6" fill="#E02D37"/>
            <circle cx="300" cy="190" r="16" fill="#E02D37" fill-opacity="0.25"/>
            <!-- Badge -->
            <text x="300" y="340" text-anchor="middle" font-family="'JetBrains Mono', monospace" font-size="12" fill="#8E95A5" letter-spacing="2">АПС ■ СОУЭ ■ ПОЖАРОТУШЕНИЕ</text>
        </svg>''',
        'service-sks.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 400" fill="none">
            <rect width="600" height="400" fill="#12151B"/>
            <!-- Server rack 19" frame -->
            <rect x="170" y="70" width="260" height="260" rx="6" fill="#151820" stroke="#FFFFFF" stroke-opacity="0.2" stroke-width="2"/>
            <!-- Mounting rails -->
            <rect x="185" y="80" width="12" height="240" fill="#222834"/>
            <rect x="403" y="80" width="12" height="240" fill="#222834"/>
            <!-- Patch panels (1U units) -->
            <g fill="#1A1E27" stroke="#FFFFFF" stroke-opacity="0.1">
                <rect x="202" y="90" width="196" height="32" rx="2"/>
                <rect x="202" y="130" width="196" height="32" rx="2"/>
                <rect x="202" y="170" width="196" height="32" rx="2"/>
                <rect x="202" y="210" width="196" height="32" rx="2"/>
                <rect x="202" y="250" width="196" height="32" rx="2"/>
            </g>
            <!-- Patch cables curving -->
            <path d="M225 110 C 235 150, 240 180, 260 220" stroke="#E02D37" stroke-width="3" stroke-linecap="round" fill="none"/>
            <path d="M245 110 C 255 140, 270 170, 290 220" stroke="#3B82F6" stroke-width="3" stroke-linecap="round" fill="none"/>
            <path d="M320 110 C 310 140, 310 180, 330 220" stroke="#10B981" stroke-width="3" stroke-linecap="round" fill="none"/>
            <path d="M350 110 C 360 150, 370 180, 380 220" stroke="#F59E0B" stroke-width="3" stroke-linecap="round" fill="none"/>
            <!-- Blinking switch activity lights -->
            <circle cx="215" cy="146" r="2.5" fill="#10B981"/>
            <circle cx="225" cy="146" r="2.5" fill="#10B981"/>
            <circle cx="235" cy="146" r="2.5" fill="#E02D37"/>
            <circle cx="245" cy="146" r="2.5" fill="#10B981"/>
            <circle cx="255" cy="146" r="2.5" fill="#10B981"/>
            <text x="300" y="360" text-anchor="middle" font-family="'JetBrains Mono', monospace" font-size="12" fill="#8E95A5" letter-spacing="2">СКС CAT 6A ■ ОПТИКА 10G</text>
        </svg>''',
        'service-electro.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 400" fill="none">
            <rect width="600" height="400" fill="#12151B"/>
            <!-- Electrical cabinet / switchboard -->
            <rect x="180" y="80" width="240" height="240" rx="8" fill="#181C24" stroke="#FFFFFF" stroke-opacity="0.18" stroke-width="2"/>
            <!-- DIN rail -->
            <rect x="200" y="130" width="200" height="10" fill="#2E3544"/>
            <rect x="200" y="210" width="200" height="10" fill="#2E3544"/>
            <!-- Modular Circuit breakers (АВВ/Schneider) -->
            <g fill="#252C3A" stroke="#FFFFFF" stroke-opacity="0.15">
                <rect x="210" y="110" width="25" height="50" rx="3"/>
                <rect x="238" y="110" width="25" height="50" rx="3"/>
                <rect x="266" y="110" width="25" height="50" rx="3"/>
                <rect x="305" y="110" width="45" height="50" rx="3"/>
                <rect x="355" y="110" width="25" height="50" rx="3"/>
                <rect x="210" y="190" width="25" height="50" rx="3"/>
                <rect x="238" y="190" width="25" height="50" rx="3"/>
                <rect x="266" y="190" width="45" height="50" rx="3"/>
                <rect x="320" y="190" width="35" height="50" rx="3"/>
            </g>
            <!-- Toggle switches -->
            <rect x="216" y="125" width="13" height="12" rx="2" fill="#E02D37"/>
            <rect x="244" y="125" width="13" height="12" rx="2" fill="#E02D37"/>
            <rect x="272" y="125" width="13" height="12" rx="2" fill="#E02D37"/>
            <!-- High voltage lightning warning symbol -->
            <path d="M300 270 L308 285 L302 285 L306 300 L294 287 L300 287 Z" fill="#F59E0B"/>
            <text x="300" y="355" text-anchor="middle" font-family="'JetBrains Mono', monospace" font-size="12" fill="#8E95A5" letter-spacing="2">0.4 кВ ■ ЩИТОВОЕ ОБОРУДОВАНИЕ</text>
        </svg>''',
        'technician-pill.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 160 80" fill="none">
            <rect width="160" height="80" rx="40" fill="#1C212B" stroke="#E02D37" stroke-width="2"/>
            <circle cx="50" cy="40" r="24" fill="#262D3B"/>
            <!-- Engineer with safety helmet icon -->
            <circle cx="50" cy="34" r="9" fill="#F59E0B"/>
            <path d="M38 31 Q50 22 62 31 Z" fill="#F59E0B"/>
            <rect x="36" y="31" width="28" height="4" rx="2" fill="#E02D37"/>
            <path d="M36 54 C36 45 42 43 50 43 C58 43 64 45 64 54" fill="#3B82F6"/>
            <!-- Tablet / switchboard -->
            <rect x="85" y="26" width="50" height="30" rx="3" fill="#0E1014" stroke="#5A6275" stroke-width="1.5"/>
            <rect x="90" y="31" width="40" height="16" fill="#18202F"/>
            <line x1="93" y1="36" x2="115" y2="36" stroke="#10B981" stroke-width="2"/>
            <line x1="93" y1="41" x2="122" y2="41" stroke="#E02D37" stroke-width="2"/>
        </svg>''',
        'camera-pill.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 160 80" fill="none">
            <rect width="160" height="80" rx="40" fill="#1C212B" stroke="#FFFFFF" stroke-opacity="0.3" stroke-width="2"/>
            <!-- PTZ Speed Dome Camera -->
            <circle cx="80" cy="38" r="24" fill="#252C3A" stroke="#FFFFFF" stroke-opacity="0.2" stroke-width="1.5"/>
            <circle cx="80" cy="38" r="14" fill="#0E1014" stroke="#E02D37" stroke-width="2"/>
            <circle cx="80" cy="38" r="5" fill="#E02D37"/>
            <circle cx="82" cy="36" r="2" fill="#FFFFFF"/>
            <path d="M60 22 L100 22 L94 15 L66 15 Z" fill="#3A4356"/>
        </svg>'''
    }

    for fname, svg in cards.items():
        with open(os.path.join(images_dir, fname), 'w', encoding='utf-8') as f:
            f.write(svg.strip())

    print(f'Generated {len(brands)} logos and {len(cards)} card visuals successfully!')

if __name__ == '__main__':
    main()
