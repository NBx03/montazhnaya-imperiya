import os

def main():
    icons_dir = r'c:\Users\hopm1\Documents\MyProjects\Python\FirstITCompanyIntern\montazhnaya-imperiya\public\icons'
    images_dir = r'c:\Users\hopm1\Documents\MyProjects\Python\FirstITCompanyIntern\montazhnaya-imperiya\public\images'
    os.makedirs(icons_dir, exist_ok=True)
    os.makedirs(images_dir, exist_ok=True)

    # 1. Exact Figma Logo: House roof + 'МИ' isometric ribbon (White M, Red И)
    logo_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 280 60" fill="none">
        <!-- Roof and ribbon icon -->
        <g transform="translate(6, 6)">
            <!-- Roof rafters -->
            <path d="M24 2 L46 17 L42 21 L24 9 L6 21 L2 17 Z" fill="#E02D37"/>
            <rect x="32" y="5" width="5" height="8" fill="#E02D37"/>
            <!-- Letter M (White 3D ribbon) -->
            <path d="M8 21 L16 16 L23 28 L23 41 L16 36 L16 27 L12 29 L12 39 L7 36 Z" fill="#FFFFFF"/>
            <path d="M16 36 L23 41 L23 49 L16 44 Z" fill="#C8CDD8"/>
            <!-- Letter И (Red 3D ribbon) -->
            <path d="M23 28 L30 16 L39 21 L39 39 L33 36 L33 28 L28 37 L23 41 Z" fill="#E02D37"/>
            <path d="M23 41 L28 37 L28 47 L23 49 Z" fill="#A81C23"/>
            <path d="M33 36 L39 39 L39 47 L33 44 Z" fill="#A81C23"/>
        </g>
        <!-- Text -->
        <text x="66" y="27" font-family="'Fira Sans Extra Condensed', 'Sofia Sans Condensed', sans-serif" font-size="24" font-weight="800" fill="#FFFFFF" letter-spacing="1">МОНТАЖНАЯ</text>
        <text x="66" y="50" font-family="'Fira Sans Extra Condensed', 'Sofia Sans Condensed', sans-serif" font-size="24" font-weight="800" fill="#E02D37" letter-spacing="1">ИМПЕРИЯ</text>
    </svg>"""

    with open(os.path.join(icons_dir, 'logo.svg'), 'w', encoding='utf-8') as f:
        f.write(logo_svg.strip())

    # 2. Hero Background SVG: server rack with bokeh LED indicator lights & subtle dark grid
    hero_bg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1920 1080" fill="none">
        <rect width="1920" height="1080" fill="#0E1014"/>
        <defs>
            <radialGradient id="hero-spot" cx="50%" cy="35%" r="55%">
                <stop offset="0%" stop-color="#E02D37" stop-opacity="0.18"/>
                <stop offset="50%" stop-color="#181216" stop-opacity="0.6"/>
                <stop offset="100%" stop-color="#0E1014" stop-opacity="1"/>
            </radialGradient>
            <linearGradient id="rack-grad" x1="0" y1="0" x2="0" y2="100%">
                <stop offset="0%" stop-color="#151922" stop-opacity="0.5"/>
                <stop offset="100%" stop-color="#0A0C0F" stop-opacity="0.95"/>
            </linearGradient>
            <filter id="blur-led" x="-50%" y="-50%" width="200%" height="200%">
                <feGaussianBlur stdDeviation="8"/>
            </filter>
        </defs>
        
        <!-- Radial atmosphere -->
        <rect width="1920" height="1080" fill="url(#hero-spot)"/>
        
        <!-- Telecom / Server rack horizontal unit slots silhouette -->
        <g opacity="0.35">
            <!-- Server rack rails and rows -->
            <rect x="0" y="320" width="1920" height="120" fill="url(#rack-grad)" stroke="#FFFFFF" stroke-opacity="0.05"/>
            <rect x="0" y="460" width="1920" height="140" fill="url(#rack-grad)" stroke="#FFFFFF" stroke-opacity="0.05"/>
            <rect x="0" y="620" width="1920" height="140" fill="url(#rack-grad)" stroke="#FFFFFF" stroke-opacity="0.05"/>
            <rect x="0" y="780" width="1920" height="160" fill="url(#rack-grad)" stroke="#FFFFFF" stroke-opacity="0.05"/>
            
            <!-- Patch ports slots in rows -->
            <path d="M 100 380 H 1820 M 100 520 H 1820 M 100 680 H 1820 M 100 840 H 1820" stroke="#FFFFFF" stroke-opacity="0.08" stroke-dasharray="8 12"/>
        </g>
        
        <!-- Glowing green & blue status LEDs (bokeh effect matching Figma rack photo) -->
        <g opacity="0.85">
            <!-- Green status LEDs -->
            <circle cx="340" cy="520" r="4" fill="#10B981" filter="url(#blur-led)"/>
            <circle cx="340" cy="520" r="2.5" fill="#34D399"/>
            <circle cx="480" cy="520" r="4" fill="#10B981" filter="url(#blur-led)"/>
            <circle cx="480" cy="520" r="2.5" fill="#34D399"/>
            <circle cx="620" cy="520" r="4" fill="#10B981" filter="url(#blur-led)"/>
            <circle cx="620" cy="520" r="2.5" fill="#34D399"/>
            <circle cx="920" cy="520" r="4" fill="#10B981" filter="url(#blur-led)"/>
            <circle cx="920" cy="520" r="2.5" fill="#34D399"/>
            <circle cx="1180" cy="520" r="4" fill="#10B981" filter="url(#blur-led)"/>
            <circle cx="1180" cy="520" r="2.5" fill="#34D399"/>
            
            <!-- Blue 10G link LEDs -->
            <circle cx="410" cy="520" r="5" fill="#3B82F6" filter="url(#blur-led)"/>
            <circle cx="410" cy="520" r="3" fill="#60A5FA"/>
            <circle cx="750" cy="520" r="5" fill="#3B82F6" filter="url(#blur-led)"/>
            <circle cx="750" cy="520" r="3" fill="#60A5FA"/>
            <circle cx="1050" cy="520" r="5" fill="#3B82F6" filter="url(#blur-led)"/>
            <circle cx="1050" cy="520" r="3" fill="#60A5FA"/>
            <circle cx="1320" cy="520" r="5" fill="#3B82F6" filter="url(#blur-led)"/>
            <circle cx="1320" cy="520" r="3" fill="#60A5FA"/>
            <circle cx="1560" cy="520" r="5" fill="#3B82F6" filter="url(#blur-led)"/>
            <circle cx="1560" cy="520" r="3" fill="#60A5FA"/>

            <!-- Second row LEDs -->
            <circle cx="360" cy="680" r="4" fill="#10B981" filter="url(#blur-led)"/>
            <circle cx="360" cy="680" r="2" fill="#34D399"/>
            <circle cx="540" cy="680" r="4" fill="#10B981" filter="url(#blur-led)"/>
            <circle cx="540" cy="680" r="2" fill="#34D399"/>
            <circle cx="880" cy="680" r="5" fill="#3B82F6" filter="url(#blur-led)"/>
            <circle cx="880" cy="680" r="3" fill="#60A5FA"/>
            <circle cx="1220" cy="680" r="4" fill="#10B981" filter="url(#blur-led)"/>
            <circle cx="1220" cy="680" r="2" fill="#34D399"/>
        </g>
        
        <!-- Fine technical grid overlay -->
        <g stroke="#FFFFFF" stroke-opacity="0.04" stroke-width="1">
            <line x1="320" y1="0" x2="320" y2="1080"/>
            <line x1="640" y1="0" x2="640" y2="1080"/>
            <line x1="960" y1="0" x2="960" y2="1080"/>
            <line x1="1280" y1="0" x2="1280" y2="1080"/>
            <line x1="1600" y1="0" x2="1600" y2="1080"/>
        </g>
    </svg>"""

    with open(os.path.join(images_dir, 'hero-rack-bg.svg'), 'w', encoding='utf-8') as f:
        f.write(hero_bg.strip())

    # 3. Realistic Visual for Fire Alarm Card (Smoke detector + Red/Gray manual call point box)
    fire_card_visual = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 240" fill="none">
        <defs>
            <radialGradient id="smoke-body" cx="40%" cy="35%" r="60%">
                <stop offset="0%" stop-color="#FFFFFF"/>
                <stop offset="70%" stop-color="#D9DCE2"/>
                <stop offset="100%" stop-color="#A5ACB8"/>
            </radialGradient>
            <filter id="shadow-fire" x="-20%" y="-20%" width="140%" height="140%">
                <feDropShadow dx="8" dy="16" stdDeviation="12" flood-color="#000000" flood-opacity="0.6"/>
            </filter>
        </defs>
        
        <g filter="url(#shadow-fire)">
            <!-- Manual Call Point Box (НАЖАТЬ ЗДЕСЬ ПРИ ПОЖАРЕ) -->
            <g transform="translate(40, 60) rotate(-18)">
                <rect x="0" y="0" width="105" height="115" rx="16" fill="#343842" stroke="#484E5C" stroke-width="2.5"/>
                <!-- Inner red inset -->
                <rect x="10" y="10" width="85" height="95" rx="10" fill="#E02D37"/>
                <rect x="18" y="18" width="69" height="50" rx="6" fill="#20242C" stroke="#FFFFFF" stroke-opacity="0.3"/>
                <text x="52" y="44" text-anchor="middle" font-family="'JetBrains Mono', monospace" font-size="12" font-weight="900" fill="#FFFFFF" letter-spacing="1">FIRE</text>
                <path d="M40 50 L64 50 M52 46 L52 54" stroke="#E02D37" stroke-width="2"/>
                <text x="52" y="86" text-anchor="middle" font-family="'Onest', sans-serif" font-size="8" font-weight="800" fill="#FFFFFF">НАЖАТЬ ЗДЕСЬ</text>
                <text x="52" y="96" text-anchor="middle" font-family="'Onest', sans-serif" font-size="9" font-weight="900" fill="#FFFFFF">ПРИ ПОЖАРЕ</text>
            </g>

            <!-- Ceiling Optical Smoke Detector (White dome) -->
            <g transform="translate(150, 40) rotate(8)">
                <!-- Outer ceiling base plate -->
                <ellipse cx="70" cy="70" rx="65" ry="65" fill="#E2E5EB" stroke="#FFFFFF" stroke-opacity="0.8" stroke-width="2"/>
                <ellipse cx="70" cy="70" rx="54" ry="54" fill="url(#smoke-body)"/>
                <!-- Air sampling slotted chamber -->
                <ellipse cx="70" cy="70" rx="36" ry="36" fill="#181B22"/>
                <ellipse cx="70" cy="70" rx="36" ry="36" stroke="#2B303C" stroke-width="8" stroke-dasharray="14 8"/>
                <ellipse cx="70" cy="70" rx="20" ry="20" fill="#DCE0E8"/>
                <!-- Red alarm beacon LED -->
                <circle cx="70" cy="70" r="4.5" fill="#E02D37"/>
                <circle cx="71.5" cy="68.5" r="1.5" fill="#FFFFFF"/>
            </g>
        </g>
    </svg>"""

    with open(os.path.join(images_dir, 'fire-card-visual.svg'), 'w', encoding='utf-8') as f:
        f.write(fire_card_visual.strip())

    # 4. Realistic Visual for SCS Card (Two Ethernet RJ45 cables with clear boots)
    sks_card_visual = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 240" fill="none">
        <defs>
            <filter id="shadow-sks" x="-20%" y="-20%" width="140%" height="140%">
                <feDropShadow dx="8" dy="16" stdDeviation="12" flood-color="#000000" flood-opacity="0.6"/>
            </filter>
            <linearGradient id="rj-metal" x1="0" y1="0" x2="1" y2="1">
                <stop offset="0%" stop-color="#FFFFFF"/>
                <stop offset="50%" stop-color="#C2C7D0"/>
                <stop offset="100%" stop-color="#7B8290"/>
            </linearGradient>
            <linearGradient id="rj-pin" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="#F59E0B"/>
                <stop offset="100%" stop-color="#B45309"/>
            </linearGradient>
        </defs>

        <g filter="url(#shadow-sks)">
            <!-- Left RJ45 Connector -->
            <g transform="translate(80, 40) rotate(-22)">
                <!-- Cable strain boot -->
                <path d="M20 120 L50 120 L45 80 L25 80 Z" fill="#4B5262"/>
                <!-- Clear plastic connector head -->
                <rect x="18" y="25" width="34" height="58" rx="4" fill="url(#rj-metal)" stroke="#FFFFFF" stroke-width="1.5"/>
                <!-- Gold contact pins (8P8C) -->
                <g fill="url(#rj-pin)">
                    <rect x="22" y="22" width="2" height="12"/>
                    <rect x="26" y="22" width="2" height="12"/>
                    <rect x="30" y="22" width="2" height="12"/>
                    <rect x="34" y="22" width="2" height="12"/>
                    <rect x="38" y="22" width="2" height="12"/>
                    <rect x="42" y="22" width="2" height="12"/>
                    <rect x="46" y="22" width="2" height="12"/>
                </g>
                <!-- Latch clip lever -->
                <path d="M35 35 L35 70 L46 65" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" fill="none"/>
            </g>

            <!-- Right RJ45 Connector -->
            <g transform="translate(190, 60) rotate(15)">
                <!-- Cable strain boot -->
                <path d="M20 120 L50 120 L45 80 L25 80 Z" fill="#373D49"/>
                <!-- Clear plastic connector head -->
                <rect x="18" y="25" width="34" height="58" rx="4" fill="url(#rj-metal)" stroke="#FFFFFF" stroke-width="1.5"/>
                <!-- Gold contact pins -->
                <g fill="url(#rj-pin)">
                    <rect x="22" y="22" width="2" height="12"/>
                    <rect x="26" y="22" width="2" height="12"/>
                    <rect x="30" y="22" width="2" height="12"/>
                    <rect x="34" y="22" width="2" height="12"/>
                    <rect x="38" y="22" width="2" height="12"/>
                    <rect x="42" y="22" width="2" height="12"/>
                    <rect x="46" y="22" width="2" height="12"/>
                </g>
                <!-- Latch clip lever -->
                <path d="M35 35 L35 70 L46 65" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" fill="none"/>
            </g>
        </g>
    </svg>"""

    with open(os.path.join(images_dir, 'sks-card-visual.svg'), 'w', encoding='utf-8') as f:
        f.write(sks_card_visual.strip())

    # 5. Realistic CCTV Dome & Phone App Visual
    cctv_card_visual = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 240" fill="none">
        <defs>
            <filter id="shadow-cctv" x="-20%" y="-20%" width="140%" height="140%">
                <feDropShadow dx="8" dy="16" stdDeviation="12" flood-color="#000000" flood-opacity="0.6"/>
            </filter>
        </defs>
        <g filter="url(#shadow-cctv)">
            <!-- Dome CCTV Camera -->
            <g transform="translate(40, 20)">
                <ellipse cx="80" cy="50" rx="75" ry="30" fill="#2B313E" stroke="#FFFFFF" stroke-opacity="0.3" stroke-width="2"/>
                <path d="M15 50 Q80 120 145 50 Z" fill="#14171E"/>
                <circle cx="80" cy="72" r="30" fill="#0A0C10" stroke="#E02D37" stroke-width="2"/>
                <circle cx="80" cy="72" r="14" fill="#1C212B"/>
                <circle cx="80" cy="72" r="6" fill="#E02D37"/>
                <circle cx="83" cy="69" r="2.5" fill="#FFFFFF"/>
            </g>
            <!-- Tilted Smartphone showing camera dashboard -->
            <g transform="translate(130, 45) rotate(14)">
                <rect x="0" y="0" width="100" height="170" rx="16" fill="#0A0D12" stroke="#4F5666" stroke-width="2.5"/>
                <!-- Screen -->
                <rect x="6" y="8" width="88" height="154" rx="10" fill="#141822"/>
                <!-- Camera view on phone -->
                <rect x="12" y="18" width="76" height="50" rx="4" fill="#202636"/>
                <circle cx="20" cy="26" r="3" fill="#E02D37"/>
                <text x="27" y="28" font-family="'JetBrains Mono', monospace" font-size="6" fill="#FFFFFF" font-weight="700">REC 4K</text>
                <!-- Analytics graphs/bars on phone screen -->
                <rect x="12" y="78" width="36" height="6" rx="2" fill="#3B82F6"/>
                <rect x="12" y="90" width="76" height="8" rx="2" fill="#2A3245"/>
                <rect x="12" y="104" width="76" height="8" rx="2" fill="#2A3245"/>
                <rect x="12" y="118" width="76" height="8" rx="2" fill="#2A3245"/>
                <rect x="12" y="132" width="76" height="20" rx="4" fill="#E02D37"/>
                <text x="50" y="145" text-anchor="middle" font-family="'JetBrains Mono', monospace" font-size="7" fill="#FFFFFF" font-weight="700">ДОСТУП OK</text>
            </g>
        </g>
    </svg>"""

    with open(os.path.join(images_dir, 'cctv-card-visual.svg'), 'w', encoding='utf-8') as f:
        f.write(cctv_card_visual.strip())

    # 6. Realistic Turnstile / SKUD Visual
    skud_card_visual = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 240" fill="none">
        <defs>
            <filter id="shadow-skud" x="-20%" y="-20%" width="140%" height="140%">
                <feDropShadow dx="8" dy="16" stdDeviation="12" flood-color="#000000" flood-opacity="0.6"/>
            </filter>
        </defs>
        <g filter="url(#shadow-skud)" transform="translate(60, 20)">
            <!-- Stainless steel speed-gate turnstile pedestal -->
            <rect x="20" y="30" width="45" height="170" rx="8" fill="#323846" stroke="#FFFFFF" stroke-opacity="0.25" stroke-width="2"/>
            <rect x="135" y="30" width="45" height="170" rx="8" fill="#323846" stroke="#FFFFFF" stroke-opacity="0.25" stroke-width="2"/>
            
            <!-- Glass barrier swing flap with red/green indicator -->
            <path d="M65 90 L100 110 L65 130 Z" fill="#38BDF8" fill-opacity="0.35" stroke="#38BDF8" stroke-width="2"/>
            <path d="M135 90 L100 110 L135 130 Z" fill="#38BDF8" fill-opacity="0.35" stroke="#38BDF8" stroke-width="2"/>
            
            <!-- Face ID Terminal / RFID screen on pedestal -->
            <rect x="26" y="45" width="33" height="50" rx="4" fill="#0A0C10" stroke="#E02D37" stroke-width="1.5"/>
            <circle cx="42" cy="65" r="9" fill="#E02D37" fill-opacity="0.2"/>
            <path d="M38 65 L41 68 L48 61" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round"/>
            <text x="42" y="86" text-anchor="middle" font-family="'JetBrains Mono', monospace" font-size="5" fill="#10B981" font-weight="700">PASS GRANTED</text>
            
            <!-- Proximity RFID badge card floating -->
            <g transform="translate(130, 25) rotate(-25)">
                <rect x="0" y="0" width="70" height="44" rx="4" fill="#FFFFFF" stroke="#E02D37" stroke-width="2"/>
                <rect x="8" y="8" width="20" height="16" rx="2" fill="#E02D37"/>
                <rect x="34" y="10" width="28" height="4" rx="1" fill="#14171E"/>
                <rect x="34" y="18" width="20" height="3" rx="1" fill="#757F92"/>
                <!-- Chip / contactless icon -->
                <path d="M52 28 A 6 6 0 0 1 52 38 M56 25 A 10 10 0 0 1 56 41" stroke="#3B82F6" stroke-width="2" fill="none"/>
            </g>
        </g>
    </svg>"""

    with open(os.path.join(images_dir, 'skud-card-visual.svg'), 'w', encoding='utf-8') as f:
        f.write(skud_card_visual.strip())

    # 7. Realistic Electrical Switchboard Visual
    electro_card_visual = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 240" fill="none">
        <defs>
            <filter id="shadow-el" x="-20%" y="-20%" width="140%" height="140%">
                <feDropShadow dx="8" dy="16" stdDeviation="12" flood-color="#000000" flood-opacity="0.6"/>
            </filter>
        </defs>
        <g filter="url(#shadow-el)" transform="translate(60, 20)">
            <!-- Cabinet box -->
            <rect x="0" y="10" width="200" height="190" rx="10" fill="#232834" stroke="#FFFFFF" stroke-opacity="0.25" stroke-width="2"/>
            <!-- DIN rail 1 -->
            <rect x="15" y="45" width="170" height="12" fill="#3D4556"/>
            <!-- DIN rail 2 -->
            <rect x="15" y="120" width="170" height="12" fill="#3D4556"/>
            <!-- Modular Circuit breakers -->
            <g fill="#303746" stroke="#FFFFFF" stroke-opacity="0.2">
                <rect x="25" y="30" width="22" height="45" rx="3"/>
                <rect x="50" y="30" width="22" height="45" rx="3"/>
                <rect x="75" y="30" width="22" height="45" rx="3"/>
                <rect x="105" y="30" width="38" height="45" rx="3"/>
                <rect x="148" y="30" width="22" height="45" rx="3"/>
                
                <rect x="25" y="105" width="22" height="45" rx="3"/>
                <rect x="50" y="105" width="22" height="45" rx="3"/>
                <rect x="75" y="105" width="38" height="45" rx="3"/>
                <rect x="120" y="105" width="30" height="45" rx="3"/>
            </g>
            <!-- Red switch toggles -->
            <rect x="30" y="42" width="12" height="10" rx="2" fill="#E02D37"/>
            <rect x="55" y="42" width="12" height="10" rx="2" fill="#E02D37"/>
            <rect x="80" y="42" width="12" height="10" rx="2" fill="#E02D37"/>
            <rect x="115" y="42" width="18" height="10" rx="2" fill="#E02D37"/>
            <!-- High voltage symbol badge -->
            <polygon points="100,165 106,177 101,177 104,188 94,179 99,179" fill="#F59E0B"/>
        </g>
    </svg>"""

    with open(os.path.join(images_dir, 'electro-card-visual.svg'), 'w', encoding='utf-8') as f:
        f.write(electro_card_visual.strip())

    # 8. Realistic Alarm Sensor Card Visual
    alarm_card_visual = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 240" fill="none">
        <defs>
            <filter id="shadow-al" x="-20%" y="-20%" width="140%" height="140%">
                <feDropShadow dx="8" dy="16" stdDeviation="12" flood-color="#000000" flood-opacity="0.6"/>
            </filter>
        </defs>
        <g filter="url(#shadow-al)" transform="translate(90, 25)">
            <!-- Motion detector body -->
            <rect x="20" y="20" width="95" height="150" rx="20" fill="#252A36" stroke="#FFFFFF" stroke-opacity="0.25" stroke-width="2"/>
            <!-- Sensor window with Fresnel lens segments -->
            <path d="M30 65 Q67 100 105 65 Q67 120 30 65 Z" fill="#363E50" stroke="#FFFFFF" stroke-opacity="0.3"/>
            <!-- Red status LED -->
            <circle cx="67.5" cy="45" r="4.5" fill="#E02D37"/>
            <!-- Radio pulse waves radiating outward -->
            <path d="M125 70 A 45 45 0 0 1 125 120" stroke="#E02D37" stroke-width="3" stroke-linecap="round" fill="none"/>
            <path d="M140 55 A 70 70 0 0 1 140 135" stroke="#E02D37" stroke-width="2.5" stroke-linecap="round" stroke-opacity="0.5" fill="none"/>
        </g>
    </svg>"""

    with open(os.path.join(images_dir, 'alarm-card-visual.svg'), 'w', encoding='utf-8') as f:
        f.write(alarm_card_visual.strip())

    # 9. Realistic Photo Pill: Electrical technician in helmet with tablet
    tech_pill_img = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 100" fill="none">
        <rect width="200" height="100" rx="50" fill="#1C212B" stroke="#E02D37" stroke-width="2"/>
        <clipPath id="pill-clip">
            <rect width="200" height="100" rx="50"/>
        </clipPath>
        <g clip-path="url(#pill-clip)">
            <!-- Background electrical panel -->
            <rect x="0" y="0" width="200" height="100" fill="#12151D"/>
            <line x1="20" y1="20" x2="180" y2="20" stroke="#2B3242" stroke-width="6"/>
            <line x1="20" y1="50" x2="180" y2="50" stroke="#2B3242" stroke-width="6"/>
            <line x1="20" y1="80" x2="180" y2="80" stroke="#2B3242" stroke-width="6"/>
            
            <!-- Technician silhouette in helmet -->
            <!-- Safety Helmet (White / Orange) -->
            <ellipse cx="90" cy="38" rx="24" ry="16" fill="#F8FAFC"/>
            <path d="M66 38 Q90 22 114 38 Z" fill="#F8FAFC"/>
            <rect x="64" y="38" width="52" height="5" rx="2" fill="#E02D37"/>
            <!-- Face profile -->
            <circle cx="90" cy="50" r="14" fill="#E2B193"/>
            <!-- Work Uniform (Navy Blue / Hi-Vis Orange stripe) -->
            <path d="M60 95 C60 68 75 62 90 62 C105 62 120 68 120 95 Z" fill="#1E293B"/>
            <path d="M72 75 L108 75" stroke="#F59E0B" stroke-width="4"/>
            <!-- Tablet with diagnostics wireframe in hands -->
            <rect x="110" y="45" width="45" height="34" rx="4" fill="#0A0C10" stroke="#E02D37" stroke-width="1.5" transform="rotate(-10 110 45)"/>
            <line x1="116" y1="55" x2="142" y2="51" stroke="#10B981" stroke-width="2"/>
            <line x1="118" y1="63" x2="136" y2="60" stroke="#38BDF8" stroke-width="2"/>
        </g>
    </svg>"""

    with open(os.path.join(images_dir, 'technician-photo-pill.svg'), 'w', encoding='utf-8') as f:
        f.write(tech_pill_img.strip())

    print('Successfully generated all accurate Figma assets!')

if __name__ == '__main__':
    main()
