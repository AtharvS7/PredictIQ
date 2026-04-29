# ═══════════════════════════════════════════════════════════════
# Predictify — Developer Makefile
# Cross-platform targets (Windows + Unix via python -c)
# ═══════════════════════════════════════════════════════════════

.PHONY: install run test security-check clean graph help

help: ## Show this help
	@echo "Predictify Developer Commands:"
	@echo "  make install         Install all dependencies"
	@echo "  make run             Start backend + frontend"
	@echo "  make test            Run full test suite"
	@echo "  make security-check  Run pre-push security scan"
	@echo "  make clean           Remove caches and build artifacts"
	@echo "  make graph           Rebuild the code-review knowledge graph"

install: ## Install backend + frontend dependencies
	python run.py --install

run: ## Start the full application (backend + frontend)
	python run.py

test: ## Run all backend tests
	cd backend && python -m pytest tests/ -v --tb=short

security-check: ## Run the pre-push security validator
	python scripts/pre_push_check.py

clean: ## Remove Python/Node caches and build artifacts
	python -c "import shutil, os; [shutil.rmtree(d, True) for d in ['backend/__pycache__', 'backend/.pytest_cache', 'frontend/dist', 'frontend/.vite', '.pytest_cache']]"
	python -c "import pathlib; [f.unlink() for f in pathlib.Path('backend').rglob('*.pyc')]"
	@echo "Cleaned build artifacts."

graph: ## Rebuild the code-review knowledge graph
	python -m code_review_graph build
	@echo "Knowledge graph rebuilt."
