# Quick Start Guide

## Setup Instructions

### 1. Run Setup Script

This will copy all necessary input files from the original folders:

```powershell
cd final
.\setup.ps1
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. (Optional) Configure Azure OpenAI

Create a `.env` file in the `final/` directory:

```env
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

### 4. Run the System

```bash
python main.py
```

## What Happens

The system will execute these stages in sequence:

1. **Exposure Aggregator** - Processes AR data
2. **Risk Scoring** - Calculates risk scores
3. **Limit Setter** - Determines credit limits
4. **Merger** - Combines all outputs
5. **Audit Logger** - Creates final audit trail

## Output Files

All outputs are saved to `data/output/`:
- `exposure_report.json` - Customer exposure aggregation
- `risk_score_output.json` - Risk scores by customer
- `credit_limit_update.json` - Credit limit decisions
- `all_agents_logs.json` - Unified workflow log
- `audit_trail.json` - Final audit trail

## Log File

Detailed execution log: `logs/agent.log`

## Troubleshooting

- **Missing files**: Run `setup.ps1` again
- **Import errors**: Run `pip install -r requirements.txt`
- **Azure OpenAI errors**: System continues without AI features

See `README.md` for complete documentation.
