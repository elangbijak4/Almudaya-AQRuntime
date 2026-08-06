"""Public ``aq`` CLI."""

import sys

import typer
from aqruntime.runtime import RuntimeCore

app = typer.Typer(add_completion=False, no_args_is_help=True)


def core() -> RuntimeCore:
    try:
        return RuntimeCore()
    except RuntimeError as error:
        typer.echo(str(error))
        raise typer.Exit(1) from error


@app.command()
def discover(query: str = typer.Argument(None, help="Optional search query filter.")) -> None:
    """Discover compatible models matching host hardware specifications."""
    data = core().discover(query=query)
    hw = data["hardware"]
    is_online = data["is_online"]
    mode_label = "Online (Live Hugging Face API)" if is_online else "Offline (Local Catalog Cache)"
    typer.echo(
        f"Hardware Specs: OS={hw['os']} | RAM Total={hw['total_ram_gb']} GB "
        f"(Available={hw['available_ram_gb']} GB) | CPU Cores={hw['cpu_cores']}"
    )
    typer.echo(f"Recommended Limit: Parameter <= {hw['max_safe_param_b']}B (FP16)")
    typer.echo(f"Catalog Source   : {mode_label}\n")
    if query:
        typer.echo(f"Filter Query     : '{query}'\n")
    typer.echo("Compatible Models:\n")
    if not data["models"]:
        typer.echo(" No matching models found.")
        return
    status_labels = {
        "COMPATIBLE": "[COMPATIBLE]",
        "HIGH_RAM": "[HIGH RAM]",
        "INCOMPATIBLE": "[INCOMPATIBLE]",
    }
    for model in data["models"]:
        label = status_labels.get(model["status"], "[UNKNOWN]")
        gated_tag = " [GATED]" if model.get("is_gated") else ""
        param = model.get("param_size_b", "?")
        ram_est = model.get("est_ram_gb", "?")
        typer.echo(f" {label:14}{gated_tag:8} {model['repo_id']:40} ({param}B params | ~{ram_est} GB RAM)")
        if model.get("description"):
            typer.echo(f"                       {model['description']}")


@app.command()
def login(token: str = typer.Argument(None, help="Hugging Face User Access Token.")) -> None:
    """Save Hugging Face User Access Token for downloading gated models."""
    if not token:
        token = typer.prompt("Enter your Hugging Face Access Token (hide input)", hide_input=True)
    if not token.strip():
        typer.echo("Token cannot be empty.")
        raise typer.Exit(1)
    core().login(token.strip())
    typer.echo("Hugging Face Access Token saved successfully.")


@app.command(name="doctor")
def setup_doctor() -> None:
    """Run pre-installation hardware requirement diagnostic and minimal model recommendation."""
    from aqruntime.setup_diagnostic import run_preinstall_check

    result = run_preinstall_check()
    hw = result["hardware"]
    req = result["minimum_requirement"]

    typer.echo("==================================================================")
    typer.echo("             AQRuntime Setup Hardware Diagnostic                  ")
    typer.echo("==================================================================")
    typer.echo(f"OS          : {hw['os']}")
    typer.echo(f"Total RAM   : {hw['total_ram_gb']:.2f} GB (Available: {hw['available_ram_gb']:.2f} GB)")
    typer.echo(f"CPU Cores   : {hw['cpu_cores']}")
    typer.echo("------------------------------------------------------------------")
    if result["is_capable"]:
        typer.echo("Status      : [PASS] System meets minimum hardware requirements.")
        typer.echo(f"Entry Model : Lightest recommended model is '{req['lightest_model']}' (~{req['lightest_model_ram_gb']} GB RAM).")
    else:
        typer.echo("Status      : [WARNING / FAIL] System is below minimum requirements!")
        typer.echo(f"Requirement : Minimum {req['min_ram_gb']} GB RAM is required for entry models.")
        typer.echo(f"Lightest Model '{req['lightest_model']}' requires ~{req['lightest_model_ram_gb']} GB RAM.")
        typer.echo("Installation or execution may experience severe slowdowns or memory exhaustion.")
    typer.echo("==================================================================")


@app.command()
def pull(
    model: str,
    token: str = typer.Option(None, "--token", "-t", help="Optional Hugging Face User Access Token."),
    yes: bool = typer.Option(False, "--yes", "-y", help="Bypass interactive download size confirmation prompt."),
) -> None:
    """Download MODEL and store it locally."""
    runtime = core()
    est_size = runtime.estimate_size(model, token=token)
    target_path = runtime.storage.path_for(model)

    typer.echo("==================================================================")
    typer.echo("                   Model Download Warning                         ")
    typer.echo("==================================================================")
    typer.echo(f"Repository ID   : {model}")
    typer.echo(f"Estimated Size  : {est_size}")
    typer.echo(f"Storage Path    : {target_path}")
    typer.echo("Notice          : This operation uses your network connection.")
    typer.echo("==================================================================")

    if not yes:
        confirm = typer.confirm("Proceed with download?", default=True)
        if not confirm:
            typer.echo("\n[!] Download canceled by user.")
            raise typer.Exit(0)

    typer.echo("\nDownloading model...")
    try:
        runtime.pull(model, token=token)
    except RuntimeError as error:
        typer.echo(str(error))
        raise typer.Exit(1) from error
    typer.echo("\nCompleted.")


@app.command(name="list")
def list_installed() -> None:
    """Display locally installed models."""
    models = core().list_models()
    if not models:
        typer.echo("No installed models.")
        return
    typer.echo("Installed Models\n")
    for model in models:
        typer.echo(f"- {model}")


@app.command()
def ui(
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="Server host IP address."),
    port: int = typer.Option(8000, "--port", "-p", help="Server port number."),
    no_browser: bool = typer.Option(False, "--no-browser", help="Do not automatically open web browser."),
) -> None:
    """Launch local HTTP server and open the Web UI Dashboard in browser."""
    from aqruntime.server.api import run_server

    run_server(host=host, port=port, runtime=core(), open_browser=not no_browser)


@app.command()
def serve(
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="Server host IP address."),
    port: int = typer.Option(8000, "--port", "-p", help="Server port number."),
) -> None:
    """Launch local OpenAI-compatible HTTP REST API Server."""
    from aqruntime.server.api import run_server

    run_server(host=host, port=port, runtime=core())


@app.command()
def run(
    model: str,
    memory: bool = typer.Option(True, "--memory/--no-memory", "-m/-nm", help="Persist conversation memory."),
    session: str = typer.Option(None, "--session", "-s", help="Custom session name for memory storage."),
    system: str = typer.Option(None, "--system", "-sys", help="Custom system prompt override."),
    max_tokens: int = typer.Option(512, "--max-tokens", "-n", help="Maximum output tokens limit (64-8192)."),
) -> None:
    """Load MODEL and start an interactive local inference session."""
    runtime = core()
    try:
        engine = runtime.load_inference(
            model, persistent=memory, session_name=session, system_prompt=system
        )
    except (FileNotFoundError, RuntimeError) as error:
        typer.echo(str(error))
        raise typer.Exit(1) from error
    mode_text = "Incognito (Ephemeral)" if not memory else f"Persistent (Session: {session or model})"
    typer.echo(f"Memory Mode: {mode_text} | Max Tokens: {max_tokens}")
    try:
        while True:
            try:
                prompt = typer.prompt("AQRuntime>")
            except (EOFError, KeyboardInterrupt):
                typer.echo("\nInteractive session terminated.")
                break
            if prompt.strip().lower() == "exit":
                typer.echo("Interactive session terminated.")
                break
            try:
                typer.echo(f"\nModel>\n\n{engine.generate(prompt, max_tokens=max_tokens)}")
            except RuntimeError as error:
                typer.echo(str(error))
    finally:
        if "engine" in locals() and engine:
            engine.unload()
        runtime.shutdown()


memory_app = typer.Typer(help="Manage saved conversation memory sessions.")
app.add_typer(memory_app, name="memory")

runtime_app = typer.Typer(help="Manage and inspect hardware execution runtimes/providers.")
app.add_typer(runtime_app, name="runtime")


@runtime_app.command(name="list")
def list_runtimes() -> None:
    """List all available hardware execution runtimes."""
    rt = core()
    typer.echo(rt.providers.format_runtime_list())


@runtime_app.command(name="info")
def info_runtime(provider: str = typer.Argument(..., help="Name of execution provider (e.g. intel-npu, intel-arc, cpu, cuda, directml).")) -> None:
    """Display detailed hardware status and capabilities of an execution provider."""
    rt = core()
    try:
        typer.echo(rt.providers.format_runtime_info(provider))
    except ValueError as err:
        typer.echo(str(err))
        raise typer.Exit(1) from err


@memory_app.command(name="list")
def list_memory_sessions() -> None:
    """List all saved conversation memory sessions."""
    sessions = core().memory_list()
    if not sessions:
        typer.echo("No saved memory sessions.")
        return
    typer.echo("Saved Memory Sessions:\n")
    for s in sessions:
        typer.echo(f"- {s['name']:30} ({s['turns']} turns | Last updated: {s['updated_at'][:19]})")


@memory_app.command(name="clear")
def clear_memory_session(session: str) -> None:
    """Clear a saved conversation memory session."""
    if core().memory_clear(session):
        typer.echo(f"Memory session '{session}' cleared.")
    else:
        typer.echo(f"Memory session '{session}' not found.")


@memory_app.command(name="export")
def export_memory_session(
    session: str,
    output: str = typer.Option(None, "--output", "-o", help="Target markdown file path."),
) -> None:
    """Export a memory session to a markdown file."""
    from pathlib import Path
    target = Path(output) if output else Path(f"memory_{session}_export.md")
    if core().memory_export(session, target):
        typer.echo(f"Memory session '{session}' exported to {target.resolve()}")
    else:
        typer.echo(f"Memory session '{session}' not found or empty.")


@app.command()
def remove(model: str) -> None:
    """Remove a locally installed MODEL."""
    runtime = core()
    if not runtime.remove(model):
        typer.echo("Model not found.")
        raise typer.Exit(1)
    typer.echo("Model removed.")


@app.command(name="help")
def help_guide() -> None:
    """Display comprehensive AQRuntime CLI command reference and user manual."""
    typer.echo("""
======================================================================
⚡ AQRuntime Open-Source CLI Command Reference & Manual (v2.4.0)
======================================================================

USAGE:
  aq <command> [options] [arguments]

CORE COMMANDS:
  aq help                           Display this comprehensive CLI user guide.
  aq ui                             Launch interactive Web Control Center UI (Tab 1-5).
  aq serve                          Launch headless OpenAI-compatible REST API server.
  aq doctor                         Run system hardware diagnostic & capability audit.
  aq discover [query|nvidia|vision|audio] Search Hugging Face model catalog online/offline.
  aq login <token>                  Authenticate & save Hugging Face access token.
  aq pull <model>                   Download & install Hugging Face model to local disk.
  aq list                           List all locally downloaded and installed models.
  aq run <model>                    Launch interactive CLI chat session with local model.
  aq remove <model>                 Delete an installed model from local storage.
  aq version                        Display current AQRuntime version.

EXECUTION PROVIDERS & HARDWARE:
  aq runtime list                   List hardware execution providers (CPU, NPU, Arc, CUDA).
  aq runtime info <provider>        Inspect hardware capabilities of a specific provider.

CONVERSATION MEMORY:
  aq memory list                    List all saved conversation memory sessions.
  aq memory clear <session>         Clear a saved conversation memory session.
  aq memory export <session> [-o]   Export a memory session to a Markdown file (.md).

OPTIONS FOR 'aq run':
  --memory, -m / --no-memory, -nm   Toggle conversation memory persistence.
  --session, -s <name>              Specify custom session name for memory storage.
  --system, -sys <prompt>           Set custom system prompt override.
  --max-tokens, -n <num>            Set maximum output tokens limit (64 to 8192).

EXAMPLES:
  $ aq discover vision
  $ aq pull bartowski/gemma-2-2b-it-GGUF
  $ aq run bartowski/gemma-2-2b-it-GGUF --max-tokens 2048
  $ aq ui
======================================================================
""")


@app.command()
def version() -> None:
    """Display the AQRuntime version."""
    typer.echo("AQRuntime")
    typer.echo(f"Version {core().settings.version}")


def main() -> None:
    # Windows consoles can default to cp1252 while model output is Unicode.
    # Replacement keeps an interactive session alive when a character is unsupported.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    app()
