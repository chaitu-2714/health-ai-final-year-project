# Data Flow Diagram (DFD)

This document maps the flow of information through the application modules, databases, and users.

---

## 1. Level 0 DFD (Context Diagram)
The Context Diagram represents the application as a single process boundary and shows external entities (User, File System, Ollama Service):

```
                       ┌───────────────────────┐
                       │                       │
                       │                       │
                       │                       ▼
┌──────────────┐  Credentials & Documents  ┌──────────────────────────┐  Generated PDF Reports  ┌──────────────┐
│              ├──────────────────────────►│                          ├────────────────────────►│  Local File  │
│     USER     │                           │   AURA HEALTH SYSTEM     │                         │    SYSTEM    │
│              │◄──────────────────────────┤                          │◄────────────────────────┤              │
└──────────────┘    Biometric Analytics    └───────────┬──────────────┘    File Data Stream     └──────────────┘
                    & Health Trends                    │      ▲
                                                       │      │
                                            Prompt &   │      │ Summary
                                           Parameters  │      │ Response
                                                       ▼      │
                                                   ┌──────────┴───────┐
                                                   │   Local Ollama   │
                                                   │   (AI Engine)    │
                                                   └──────────────────┘
```

---

## 2. Level 1 DFD (Module Level Flows)
The Level 1 diagram breaks the system into distinct operational bubbles, data stores, and data movements:

```mermaid
graph TD
    User([User])
    
    %% Processes
    P1[1.0 Authenticate User]
    P2[2.0 Upload & Validate File]
    P3[3.0 OCR Text Extraction]
    P4[4.0 Parameter Parsing]
    P5[5.0 Reference Comparison]
    P6[6.0 AI Summarization]
    P7[7.0 Query & Search History]
    P8[8.0 Export PDF Report]

    %% Data Stores
    D1[(Users DB)]
    D2[(Reports DB)]
    D3[(Parameters DB)]
    D4[(Analysis DB)]
    D5[(History DB)]
    D6[(Local Filesystem)]

    %% External Services
    Ollama[Local Ollama API]

    %% Data Flows
    User -->|Credentials| P1
    P1 -->|Read/Write| D1
    P1 -->|Session Confirmed| User

    User -->|Selects File| P2
    P2 -->|Save Report Row| D2
    P2 -->|Write Audit Log| D5
    P2 -->|Image Data| P3
    
    P3 -->|OpenCV Clean/Tesseract| P3
    P3 -->|Raw Text Preview| User
    User -->|Corrected Text| P4

    P4 -->|Regex & spaCy Matches| D3
    D3 -->|Parameters| P5
    P5 -->|Check Boundaries| D4
    
    D3 & D4 -->|Biometric values & classes| P6
    Ollama -->|AI Inference| P6
    P6 -->|Query Model API| Ollama
    P6 -->|Clinician Summary| User

    User -->|Filter Search Specs| P7
    P7 -->|Read History/Reports| D2 & D4 & D5
    P7 -->|History Logs Table| User

    User -->|Export Command| P8
    P8 -->|Query Values| D2 & D3 & D4
    P8 -->|Build Document PDF| D6
    P8 -->|Log PDF Export| D5
```
