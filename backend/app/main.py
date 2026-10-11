"""FastAPI routes. Only /health works so far; the rest are stubs."""

from fastapi import FastAPI, HTTPException

from app.schemas import (
    AnalysisResult,
    AnalyzeRequest,
    BatchAnalyzeRequest,
    BatchAnalyzeResponse,
)

app = FastAPI(
    title="Ambiguous Requirements Detector",
    description="Detects and corrects ambiguous software requirements using LLMs.",
)

NOT_IMPLEMENTED = "Not implemented yet"


@app.get("/health")
def health() -> dict[str, str]:
    """Report that the server is running."""
    return {"status": "ok"}


@app.post("/analyze", response_model=AnalysisResult)
def analyze(request: AnalyzeRequest) -> AnalysisResult:
    """Analyze a single requirement."""
    raise HTTPException(status_code=501, detail=NOT_IMPLEMENTED)


@app.post("/analyze/batch", response_model=BatchAnalyzeResponse)
def analyze_batch(request: BatchAnalyzeRequest) -> BatchAnalyzeResponse:
    """Analyze a whole document."""
    raise HTTPException(status_code=501, detail=NOT_IMPLEMENTED)


@app.get("/results/{run_id}", response_model=BatchAnalyzeResponse)
def get_results(run_id: str) -> BatchAnalyzeResponse:
    """Fetch the results of a past run."""
    raise HTTPException(status_code=501, detail=NOT_IMPLEMENTED)


@app.post("/evaluate")
def evaluate() -> dict:
    """Run the pipeline on the labeled dataset and return metrics."""
    raise HTTPException(status_code=501, detail=NOT_IMPLEMENTED)
