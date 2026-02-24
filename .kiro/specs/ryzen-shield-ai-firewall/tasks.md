# Implementation Plan: RyzenShield AI Firewall

## Overview

This implementation plan breaks down the RyzenShield AI Firewall into discrete coding tasks. The system consists of five main components: Detection Engine (Python), Local HTTPS Proxy (Python), Browser Extension (TypeScript), Red Team Simulator (Python), and Local Dashboard (FastAPI + React). Implementation follows a bottom-up approach, starting with core detection capabilities and building up to user-facing components.

## Tasks

- [ ] 1. Set up project structure and dependencies
  - Create directory structure for all components (detection_engine, proxy, extension, dashboard, redteam)
  - Create Python virtual environment and requirements.txt with ONNX Runtime, transformers, numpy, mitmproxy, fastapi, llama-cpp-python
  - Create package.json for browser extension with TypeScript, webpack, and Chrome extension types
  - Create package.json for dashboard frontend with React, TypeScript, Chart.js
  - Set up .gitignore for Python, Node.js, and model files
  - _Requirements: 18.1, 18.2, 14.1, 14.2, 14.3_

- [ ] 2. Implement model management system
  - [ ] 2.1 Create model downloader with Hugging Face Hub integration
    - Implement download_model() function that fetches Prompt Guard 2 22M ONNX model
    - Implement download_model() function that fetches Llama 3.2 3B Q4_K_M GGUF model
    - Add SHA256 checksum verification for downloaded models
    - Implement retry logic with exponential backoff (3 attempts)
    - Store models in local directory (./models/)
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_
  
  - [ ]* 2.2 Write unit tests for model downloader
    - Test successful download with mocked HTTP responses
    - Test checksum verification failure handling
    - Test retry logic with network failures
    - _Requirements: 11.3, 11.4_

- [ ] 3. Implement PII detection and stripping
  - [ ] 3.1 Create PIIDetector class with regex patterns
    - Implement regex patterns for email, phone, SSN, credit card, address
    - Implement process() method that detects and replaces PII with placeholders
    - Return list of PIIDetail objects with type and count
    - Preserve prompt semantic meaning after replacement
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_
  
  - [ ]* 3.2 Write property test for PII detection
    - **Property 1: PII removal completeness**
    - **Validates: Requirements 5.2, 5.3**
    - Generate random prompts with embedded PII
    - Verify all PII instances are replaced with placeholders
  
  - [ ]* 3.3 Write unit tests for PII detector
    - Test email detection and replacement
    - Test phone number detection (multiple formats)
    - Test credit card detection
    - Test address detection
    - Test semantic preservation
    - _Requirements: 5.3, 5.5_

- [ ] 4. Implement Detection Engine core
  - [ ] 4.1 Create DetectionEngine class with ONNX Runtime initialization
    - Implement _create_onnx_session() with NPU provider detection (DirectML for Windows, ROCm for Linux)
    - Implement CPU fallback when NPU unavailable
    - Load Llama tokenizer from Hugging Face transformers
    - Log active execution provider at startup
    - _Requirements: 3.1, 4.1, 4.2, 4.3, 4.5_
  
  - [ ] 4.2 Implement tokenization and normalization
    - Implement Unicode NFC normalization
    - Tokenize using Llama tokenizer with 512 token max length
    - Handle truncation for prompts exceeding 512 tokens
    - Handle special tokens and control characters
    - _Requirements: 20.1, 20.2, 20.3, 20.4, 20.5_
  
  - [ ] 4.3 Implement analyze_prompt() pipeline
    - Call PIIDetector.process() for PII detection and stripping
    - Tokenize sanitized prompt
    - Run ONNX inference on NPU/CPU
    - Measure inference latency
    - Return DetectionResponse with risk score and metadata
    - _Requirements: 3.2, 3.3, 3.4, 3.5_
  
  - [ ]* 4.4 Write property test for tokenization
    - **Property 2: Tokenization consistency**
    - **Validates: Requirements 20.2, 20.5**
    - Generate random text inputs
    - Verify tokenization produces consistent results for same input
    - Verify semantic meaning preserved after normalization
  
  - [ ]* 4.5 Write unit tests for Detection Engine
    - Test NPU provider detection on Windows and Linux
    - Test CPU fallback when NPU unavailable
    - Test tokenization with various input lengths
    - Test inference latency measurement
    - _Requirements: 4.1, 4.2, 4.3_

- [ ] 5. Implement risk scoring and action determination
  - [ ] 5.1 Create RiskScorer class
    - Implement calculate() method that converts logits to 0-100 risk score using softmax
    - Implement determine_action() method that maps risk scores to actions (allow/sanitize/block/alert)
    - Use configurable thresholds: 0-29 allow, 30-59 sanitize, 60-84 block, 85-100 alert
    - _Requirements: 6.1, 6.2, 6.3, 6.4_
  
  - [ ]* 5.2 Write property test for risk scoring
    - **Property 3: Risk score monotonicity**
    - **Validates: Requirements 6.1, 6.2, 6.3, 6.4**
    - Generate random logits
    - Verify higher jailbreak logits produce higher risk scores
    - Verify risk scores always in 0-100 range
  
  - [ ]* 5.3 Write unit tests for RiskScorer
    - Test softmax calculation correctness
    - Test risk score calculation for known logits
    - Test action determination for each threshold range
    - Test boundary conditions (29/30, 59/60, 84/85)
    - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [ ] 6. Checkpoint - Ensure Detection Engine tests pass
  - Run all Detection Engine unit tests and property tests
  - Verify NPU detection works on target hardware
  - Verify inference latency meets <20ms requirement
  - Ask the user if questions arise

- [ ] 7. Implement configuration management
  - [ ] 7.1 Create SystemConfiguration dataclass and config file loader
    - Define SystemConfiguration dataclass with all settings (risk thresholds, performance, PII, logging, proxy, dashboard)
    - Implement load_config() that reads from YAML/JSON file
    - Implement validate_config() that checks value ranges and types
    - Implement reload_config() that hot-reloads without restart
    - Use default values when config file missing or invalid
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_
  
  - [ ]* 7.2 Write unit tests for configuration management
    - Test config loading from valid file
    - Test validation rejection of invalid values
    - Test default value fallback
    - Test hot-reload functionality
    - _Requirements: 12.2, 12.3, 12.5_

- [ ] 8. Implement error handling and resilience
  - [ ] 8.1 Add error handling to Detection Engine
    - Wrap analyze_prompt() in try-except that logs errors and returns allow action
    - Implement circuit breaker pattern (3 consecutive failures trigger fail-open mode)
    - Add fail-open mode flag that bypasses detection when active
    - Log all errors with full stack traces
    - _Requirements: 17.1, 17.2, 17.3, 17.4, 17.5_
  
  - [ ]* 8.2 Write unit tests for error handling
    - Test error logging and fail-open behavior
    - Test circuit breaker activation after 3 failures
    - Test circuit breaker reset after successful inference
    - Test NPU fallback to CPU on NPU errors
    - _Requirements: 17.1, 17.2, 17.4_

- [ ] 9. Implement Local HTTPS Proxy
  - [ ] 9.1 Create ProxyInterceptor class with mitmproxy
    - Implement request() method that intercepts outgoing HTTPS requests
    - Implement APIEndpointMatcher that checks if URL matches supported AI APIs (OpenAI, Anthropic, Google)
    - Implement extract_prompt() that parses JSON request bodies and extracts prompt text
    - Forward extracted prompts to DetectionEngine.analyze_prompt()
    - Apply response actions: allow (forward), sanitize (modify body), block (return 403)
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 13.3, 13.4_
  
  - [ ] 9.2 Implement certificate management
    - Create CertificateManager class that generates local CA certificate
    - Implement install_ca_to_system() for Windows (certutil) and Linux (update-ca-certificates)
    - Store CA certificate in user config directory
    - _Requirements: 18.3_
  
  - [ ] 9.3 Implement proxy logging
    - Log all interception events to SQLite database
    - Record timestamp, URL, application, risk score, action, latency
    - Handle TLS decryption failures gracefully (log and pass through)
    - _Requirements: 2.5, 17.1_
  
  - [ ]* 9.4 Write unit tests for proxy interceptor
    - Test endpoint matching for OpenAI, Anthropic, Google APIs
    - Test prompt extraction from JSON payloads
    - Test request modification for sanitize action
    - Test request blocking for block action
    - Test TLS failure pass-through
    - _Requirements: 2.1, 2.2, 2.4, 2.5_

- [ ] 10. Implement Browser Extension (Manifest V3)
  - [ ] 10.1 Create extension manifest and project structure
    - Create manifest.json with Manifest V3 specification
    - Declare permissions: webRequest, storage, notifications, nativeMessaging
    - Declare host_permissions for ChatGPT, Claude, Gemini, Copilot domains
    - Set up TypeScript build configuration with webpack
    - _Requirements: 19.1, 19.2, 19.3, 19.4, 19.5_
  
  - [ ] 10.2 Implement content script for prompt interception
    - Create content.js that intercepts form submissions on AI application pages
    - Intercept fetch() and XMLHttpRequest calls to AI APIs
    - Extract prompt text from request payloads
    - Send PromptInterceptionRequest to background service worker
    - _Requirements: 1.1, 1.2, 13.1, 13.2_
  
  - [ ] 10.3 Implement background service worker
    - Create background.js service worker that receives interception requests
    - Communicate with Detection Engine via native messaging (or local HTTP API)
    - Receive DetectionResponse and apply action (allow/sanitize/block/alert)
    - Store interception events in chrome.storage.local
    - _Requirements: 1.3, 1.4, 1.5_
  
  - [ ] 10.4 Implement user notifications
    - Display browser notification for blocked prompts with risk score and reason
    - Display inline warning for sanitized prompts showing modifications
    - Display critical alert modal for 85-100 risk scores with educational content
    - Add link to Dashboard in all notifications
    - Record notification dismissals
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_
  
  - [ ]* 10.5 Write unit tests for extension components
    - Test prompt extraction from various AI application DOM structures
    - Test fetch/XHR interception
    - Test notification display logic
    - Test storage operations
    - _Requirements: 1.1, 1.2, 7.1, 7.2_

- [ ] 11. Checkpoint - Ensure proxy and extension tests pass
  - Run all proxy and extension unit tests
  - Manually test certificate installation on Windows and Linux
  - Manually test extension loading in Chrome/Edge/Firefox
  - Ask the user if questions arise

- [ ] 12. Implement SQLite data storage
  - [ ] 12.1 Create database schema and initialization
    - Create SQLite database with tables: prompt_logs, pii_detections, threat_detections, redteam_simulations, redteam_results, performance_metrics
    - Create indexes on timestamp, risk_score, action columns
    - Implement database initialization function
    - _Requirements: 8.1, 8.5_
  
  - [ ] 12.2 Implement log storage functions
    - Implement insert_prompt_log() that stores PromptAnalysisRecord
    - Implement insert_pii_detection() for PII details
    - Implement insert_threat_detection() for threat details
    - Implement query_logs() with filtering by date, risk score, action
    - Implement log retention cleanup (delete logs older than configured days)
    - _Requirements: 8.1, 8.2, 8.5, 12.1_
  
  - [ ]* 12.3 Write unit tests for data storage
    - Test log insertion and retrieval
    - Test filtering and pagination
    - Test log retention cleanup
    - _Requirements: 8.1, 8.2_

- [ ] 13. Implement Dashboard backend API
  - [ ] 13.1 Create FastAPI application with endpoints
    - Implement GET /api/logs with pagination and filtering
    - Implement GET /api/metrics/summary for aggregate statistics
    - Implement GET /api/metrics/performance for latency percentiles
    - Implement GET /api/redteam/reports for simulation results
    - Implement GET /api/system/status for health check
    - Enable CORS for localhost frontend
    - _Requirements: 8.1, 8.2, 8.3, 8.4_
  
  - [ ] 13.2 Implement metrics calculation
    - Calculate total prompts, allowed, sanitized, blocked, critical alerts
    - Calculate average risk score
    - Calculate latency percentiles (p50, p95, p99) from performance_metrics table
    - Calculate NPU utilization and memory usage
    - _Requirements: 8.3, 16.2, 16.5_
  
  - [ ]* 13.3 Write unit tests for API endpoints
    - Test log retrieval with various filters
    - Test metrics calculation correctness
    - Test pagination logic
    - _Requirements: 8.1, 8.2, 8.3_

- [ ] 14. Implement Dashboard frontend UI
  - [ ] 14.1 Create React application structure
    - Set up React with TypeScript and React Router
    - Create components: LogList, LogDetail, MetricsSummary, PerformanceChart, RedTeamReport
    - Set up Chart.js for visualizations
    - _Requirements: 8.1, 8.2, 8.3, 8.4_
  
  - [ ] 14.2 Implement log viewing interface
    - Create LogList component that fetches and displays prompt logs
    - Implement pagination and filtering controls
    - Create LogDetail component that shows full prompt analysis
    - Add search functionality
    - _Requirements: 8.1, 8.2_
  
  - [ ] 14.3 Implement metrics dashboard
    - Create MetricsSummary component showing aggregate statistics
    - Create PerformanceChart component with latency percentile visualization
    - Display NPU utilization and memory usage
    - Add time range selector (24h, 7d, 30d)
    - _Requirements: 8.3, 16.2, 16.5_
  
  - [ ] 14.4 Implement red team report viewer
    - Create RedTeamReport component showing detection rates
    - Display breakdown by attack technique category
    - Show historical detection rate chart
    - _Requirements: 10.1, 10.2, 10.3, 10.4_

- [ ] 15. Implement Red Team Simulator
  - [ ] 15.1 Create JailbreakTechniqueDatabase with 50+ techniques
    - Define JailbreakTechnique dataclass with name, category, description, example
    - Populate database with techniques: DAN, prefix injection, token smuggling, role play, encoding, etc.
    - Organize techniques into categories: role_play, injection, encoding, manipulation, etc.
    - _Requirements: 9.2_
  
  - [ ] 15.2 Implement RedTeamSimulator class
    - Load Llama 3.2 3B model using llama-cpp-python
    - Implement _generate_adversarial_prompt() that uses LLM to create variants
    - Implement run_simulation() that generates prompts for all techniques
    - Submit generated prompts to DetectionEngine and record results
    - Calculate detection rate (detected / total)
    - _Requirements: 9.1, 9.2, 9.3, 9.4_
  
  - [ ] 15.3 Implement simulation reporting
    - Store simulation results in redteam_simulations and redteam_results tables
    - Generate SimulationReport with detection rate and breakdown by category
    - Display warning notification when detection rate < 95%
    - _Requirements: 9.5, 10.1, 10.2_
  
  - [ ]* 15.4 Write unit tests for Red Team Simulator
    - Test technique database retrieval
    - Test simulation result recording
    - Test detection rate calculation
    - _Requirements: 9.2, 9.4, 10.1_

- [ ] 16. Implement performance monitoring
  - [ ] 16.1 Add performance instrumentation
    - Measure and log inference latency for every prompt analysis
    - Measure and log PII detection time, tokenization time separately
    - Record execution provider (NPU/CPU) for each inference
    - Store metrics in performance_metrics table
    - _Requirements: 16.1, 3.5_
  
  - [ ] 16.2 Implement performance warning system
    - Check if inference latency exceeds 50ms threshold
    - Log performance warning when threshold exceeded
    - Display warning in Dashboard when p95 latency > 50ms
    - _Requirements: 16.4_
  
  - [ ]* 16.3 Write unit tests for performance monitoring
    - Test latency measurement accuracy
    - Test warning trigger logic
    - Test metrics storage
    - _Requirements: 16.1, 16.4_

- [ ] 17. Checkpoint - Ensure all components integrated
  - Run end-to-end test: browser extension → detection engine → dashboard
  - Run end-to-end test: proxy → detection engine → dashboard
  - Verify logs appear in Dashboard
  - Verify metrics calculated correctly
  - Ask the user if questions arise

- [ ] 18. Implement installation and setup
  - [ ] 18.1 Create installation scripts
    - Create install.sh for Linux (install dependencies, set up virtual environment, download models, install CA certificate)
    - Create install.ps1 for Windows (install dependencies, set up virtual environment, download models, install CA certificate)
    - Create setup wizard script that guides through initial configuration
    - _Requirements: 18.1, 18.2, 18.3, 18.4_
  
  - [ ] 18.2 Create startup scripts
    - Create start.sh / start.ps1 that launches all components (proxy, dashboard, red team scheduler)
    - Add systemd service file for Linux
    - Add Windows service configuration
    - _Requirements: 14.1, 14.2_
  
  - [ ]* 18.3 Write installation documentation
    - Document installation steps for Windows and Linux
    - Document browser extension installation
    - Document proxy configuration for applications
    - _Requirements: 18.4, 18.5_

- [ ] 19. Implement supported application detection
  - [ ] 19.1 Create application detection for browser extension
    - Maintain list of supported domains: chat.openai.com, claude.ai, gemini.google.com, copilot.microsoft.com
    - Implement domain matching in content script
    - Activate interception only on supported domains
    - _Requirements: 13.1, 13.2, 13.5_
  
  - [ ] 19.2 Create API endpoint detection for proxy
    - Maintain list of API endpoint patterns with regex
    - Implement endpoint matching in ProxyInterceptor
    - Support OpenAI, Anthropic, Google Generative AI APIs
    - _Requirements: 13.3, 13.4, 13.5_
  
  - [ ]* 19.3 Write unit tests for application detection
    - Test domain matching for all supported applications
    - Test API endpoint pattern matching
    - Test non-matching URLs pass through
    - _Requirements: 13.1, 13.2, 13.3, 13.4_

- [ ] 20. Implement privacy audit mode
  - [ ] 20.1 Add network connection logging
    - Log all outbound network connections with destination, purpose, timestamp
    - Store network logs in separate table
    - Implement privacy_audit_mode flag in configuration
    - Display network log in Dashboard when audit mode enabled
    - _Requirements: 15.3, 15.5_
  
  - [ ]* 20.2 Write unit tests for privacy audit
    - Test network connection logging
    - Test audit mode flag behavior
    - _Requirements: 15.5_

- [ ] 21. Final integration and testing
  - [ ] 21.1 Create end-to-end integration tests
    - Test full flow: user submits prompt → interception → detection → notification → logging
    - Test all risk score ranges and corresponding actions
    - Test PII detection and stripping in full flow
    - Test red team simulation execution
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 2.3, 2.4, 3.1, 3.2, 3.3, 3.4, 6.1, 6.2, 6.3, 6.4_
  
  - [ ] 21.2 Verify performance requirements
    - Measure inference latency on AMD Ryzen AI hardware (target: <20ms p95)
    - Measure NPU throughput (target: 50 TOPS)
    - Verify detection rate on known jailbreak dataset (target: >95%)
    - _Requirements: 3.5, 4.4, 6.5_
  
  - [ ] 21.3 Verify cross-platform compatibility
    - Test on Windows 10/11 with DirectML NPU provider
    - Test on Linux (Ubuntu 22.04) with ROCm NPU provider
    - Test browser extension on Chrome, Edge, Firefox
    - _Requirements: 14.1, 14.2, 14.3_

- [ ] 22. Final checkpoint - Complete system validation
  - Ensure all tests pass
  - Verify installation scripts work on clean systems
  - Verify all requirements are met
  - Ask the user if questions arise

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at major milestones
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- The implementation uses Python for backend components and TypeScript for frontend components
- NPU acceleration is critical for performance - test on actual AMD Ryzen AI hardware
- Privacy is paramount - all processing must remain on-device
