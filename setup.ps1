# Setup Script for Customer Credit Assessment System
# This script copies necessary input files from original folders to the final system

Write-Host "=" * 80
Write-Host "Customer Credit Assessment System - Setup Script"
Write-Host "=" * 80
Write-Host ""

$baseDir = "c:\Users\golla.pranay\Desktop\CreditAssessment"
$finalInputDir = "$baseDir\final\data\input"

Write-Host "Creating input directory structure..."
New-Item -ItemType Directory -Force -Path $finalInputDir | Out-Null

Write-Host ""
Write-Host "Copying input files from original folders..."
Write-Host ""

# Files from folder 1 (Exposure Aggregator)
Write-Host "[1/6] Copying customer_id_list.csv..."
Copy-Item "$baseDir\1\Exposure.aggregator\Inputs\customer_id_list.csv" "$finalInputDir\" -Force

Write-Host "[2/6] Copying ERP_AR_extract.json..."
Copy-Item "$baseDir\1\Exposure.aggregator\Data_Sources\ERP_AR_extract.json" "$finalInputDir\" -Force

Write-Host "[3/6] Copying open_AR_records_sample.csv..."
Copy-Item "$baseDir\1\Exposure.aggregator\Inputs\open_AR_records_sample.csv" "$finalInputDir\" -Force

# Files from folder 2 (Risk Scoring)
Write-Host "[4/6] Copying payment_history.csv..."
Copy-Item "$baseDir\2\Inputs\payment_history.csv" "$finalInputDir\" -Force

Write-Host "[5/6] Copying credit_bureau_api_response.json..."
Copy-Item "$baseDir\2\Data_Sources\credit_bureau_api_response(Optional).json" "$finalInputDir\credit_bureau_api_response.json" -Force

# Files from merge3-4 (Limit Setter)
Write-Host "[6/6] Copying ERP_customer_master.json..."
Copy-Item "$baseDir\merge3-4\data\input\ERP_customer_master.json" "$finalInputDir\" -Force

Write-Host ""
Write-Host "=" * 80
Write-Host "Setup Complete!"
Write-Host "=" * 80
Write-Host ""
Write-Host "All input files have been copied to: $finalInputDir"
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. (Optional) Create .env file with Azure OpenAI credentials"
Write-Host "  2. Install dependencies: pip install -r requirements.txt"
Write-Host "  3. Run the system: python main.py"
Write-Host ""
Write-Host "=" * 80
