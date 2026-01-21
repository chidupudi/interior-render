# Interior Design System

AI-powered web-based interior design system using Google Gemini and Blender for 3D visualization.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              BROWSER (Client)                                │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Frontend (HTML/CSS/JS)                                              │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌────────────────────────────┐ │    │
│  │  │ Upload Panel │  │ Prompt Input │  │ Three.js 3D Viewer        │ │    │
│  │  │ (PNG/SVG)    │  │ (NL Design)  │  │ (GLB Rendering)           │ │    │
│  │  └──────────────┘  └──────────────┘  └────────────────────────────┘ │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                              HTTP/REST API
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         GCP GPU VM (Backend)                                 │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  FastAPI Backend                                                     │    │
│  │  ┌────────────────┐  ┌─────────────────┐  ┌─────────────────────┐   │    │
│  │  │ Upload Handler │  │ Gemini Service  │  │ Blender Service     │   │    │
│  │  │ /api/upload    │  │ Intent→Actions  │  │ Scene Processing    │   │    │
│  │  └────────────────┘  └────────┬────────┘  └──────────┬──────────┘   │    │
│  │                               │                       │              │    │
│  │  ┌────────────────────────────┴───────────────────────┴──────────┐   │    │
│  │  │                     Scene Manager                              │   │    │
│  │  │              (In-Memory + File Persistence)                    │   │    │
│  │  └────────────────────────────────────────────────────────────────┘   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                     │                                        │
│                            Subprocess Call                                   │
│                                     │                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Blender (GPU Accelerated)                                          │    │
│  │  ┌──────────────────────────────────────────────────────────────┐   │    │
│  │  │  scene_processor.py                                           │   │    │
│  │  │  • Load base scene                                            │   │    │
│  │  │  • Apply structured commands                                  │   │    │
│  │  │  • Export optimized GLB                                       │   │    │
│  │  └──────────────────────────────────────────────────────────────┘   │    │
│  │                              │                                       │    │
│  │  ┌──────────────────────────────────────────────────────────────┐   │    │
│  │  │  Asset Library (Predefined GLB Models)                        │   │    │
│  │  │  doors/ windows/ tv_units/ tables/ cabinets/ wardrobes/       │   │    │
│  │  └──────────────────────────────────────────────────────────────┘   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                     │                                        │
│                              GLB Output                                      │
│                                     │                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Static File Server (/models/*.glb)                                  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Data Flow

```
1. User uploads floor plan (PNG/SVG)
   └─→ POST /api/upload-layout
       └─→ Create session + initial scene state
           └─→ Blender generates base 3D model
               └─→ Return session_id + model_url

2. User enters design prompt ("Paint living room blue")
   └─→ POST /api/design { session_id, prompt }
       └─→ Gemini translates to structured actions:
           {
             "actions": [
               { "tool": "set_wall_color",
                 "parameters": { "room_id": "living_room", "hex_color": "#4169E1" }
               }
             ]
           }
       └─→ Backend validates actions against constraints
       └─→ Scene Manager updates state
       └─→ Blender applies changes + exports GLB
       └─→ Return updated model_url

3. Frontend fetches new GLB
   └─→ Three.js loads and renders model
       └─→ User sees updated 3D view
```

## Project Structure

```
interior-design/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── models/
│   │   │   └── schemas.py       # Pydantic models
│   │   ├── services/
│   │   │   ├── gemini_service.py    # Gemini API integration
│   │   │   ├── blender_service.py   # Blender orchestration
│   │   │   └── scene_manager.py     # Scene state management
│   │   └── utils/
│   │       ├── config.py        # Configuration
│   │       └── asset_library.py # Asset definitions
│   └── requirements.txt
│
├── blender/
│   ├── scripts/
│   │   ├── scene_processor.py   # Main Blender automation
│   │   └── generate_placeholder_assets.py
│   └── assets/
│       └── models/              # GLB asset library
│           ├── doors/
│           ├── windows/
│           ├── tv_units/
│           ├── tables/
│           ├── kitchen_cabinets/
│           ├── bedroom_wardrobes/
│           └── computer_tables/
│
├── frontend/
│   ├── index.html               # Single-page application
│   └── src/
│       ├── app.js               # Three.js viewer + API client
│       └── styles.css           # UI styles
│
├── deploy/
│   ├── scripts/
│   │   ├── create-gcp-vm.sh     # Create GCP GPU VM
│   │   ├── setup-gcp-vm.sh      # Setup VM dependencies
│   │   └── deploy-to-vm.sh      # Deploy application
│   └── config/
│       ├── nginx.conf           # Nginx configuration
│       └── interior-design.service  # Systemd service
│
├── docker-compose.yml           # Docker deployment
├── Dockerfile                   # Docker image
├── run-local.sh                 # Local development (Linux/Mac)
├── run-local.bat                # Local development (Windows)
└── .env.example                 # Environment template
```

## Gemini Output Contract

Gemini outputs STRICT JSON with these tools only:

```json
{
  "actions": [
    {
      "tool": "set_wall_color",
      "parameters": { "room_id": "living_room", "hex_color": "#4169E1" }
    },
    {
      "tool": "add_asset",
      "parameters": { "asset_type": "tv_units", "asset_id": "tv_unit_modern_01", "room_id": "living_room" }
    },
    {
      "tool": "replace_asset",
      "parameters": { "asset_id": "wardrobe_1", "new_asset_id": "wardrobe_sliding_02" }
    },
    {
      "tool": "move_asset",
      "parameters": { "asset_id": "table_1", "x": 3.5, "y": 2.0, "rotation": 90 }
    },
    {
      "tool": "remove_asset",
      "parameters": { "asset_id": "coffee_table_1" }
    }
  ]
}
```

Error response for constraint violations:
```json
{
  "error": "Request not allowed by system constraints"
}
```

## Constraints

### Apartment Types
- 2BHK only
- 3BHK only
- Single floor only (NO duplex, NO stairs)

### Editable Elements
- Doors
- Windows
- Wall colors
- TV units
- Tables
- Kitchen cabinets
- Bedroom wardrobes
- Computer tables

### Non-Goals
- No structural wall movement
- No custom/generated assets
- No AI-generated geometry
- No multi-floor designs

## Quick Start

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/your-org/interior-design.git
cd interior-design
```

2. Copy environment file:
```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

3. Run locally:
```bash
# Linux/Mac
./run-local.sh

# Windows
run-local.bat
```

4. Open `frontend/index.html` in your browser

### GCP Deployment

1. Set your GCP project:
```bash
export GCP_PROJECT_ID=your-project-id
```

2. Create GPU VM:
```bash
./deploy/scripts/create-gcp-vm.sh
```

3. SSH into VM and run setup:
```bash
gcloud compute ssh interior-design-gpu --zone=us-central1-a
sudo bash /path/to/setup-gcp-vm.sh
```

4. Deploy application:
```bash
./deploy/scripts/deploy-to-vm.sh
```

### Docker Deployment

```bash
# Set API key
export GEMINI_API_KEY=your-api-key

# Start services
docker-compose up -d

# Access at http://localhost
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/api/health` | Detailed health status |
| POST | `/api/upload-layout` | Upload floor plan |
| POST | `/api/design` | Apply design prompt |
| GET | `/api/scene/{session_id}` | Get scene state |
| GET | `/api/assets` | List available assets |
| GET | `/api/model/{session_id}` | Download GLB model |
| DELETE | `/api/session/{session_id}` | Delete session |

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GEMINI_API_KEY` | Yes | - | Google Gemini API key |
| `BLENDER_PATH` | No | `/usr/local/bin/blender` | Blender executable |
| `OUTPUT_DIR` | No | `./output` | Generated GLB files |
| `SCENES_DIR` | No | `./scenes` | Scene state files |
| `UPLOADS_DIR` | No | `./uploads` | Uploaded layouts |
| `USE_MOCK_BLENDER` | No | `false` | Use mock Blender service |
| `USE_MOCK_GEMINI` | No | `false` | Use mock Gemini service |

## Technology Stack

- **Frontend**: Vanilla JS, Three.js (GLB viewer)
- **Backend**: Python 3.11, FastAPI
- **3D Engine**: Blender 4.0 (headless)
- **LLM**: Google Gemini 1.5 Flash
- **Cloud**: Google Cloud Platform (GPU VM)
- **GPU**: NVIDIA T4

## License

MIT License
