import argparse
from typing import Optional, Dict, Callable
from .util import add_figure_route, set_env
import os


class MCPCLI:
    """Base class for CLI applications with support for dynamic modules and parameters."""

    def __init__(self, name: str, help_text: str, mcp=None, manager=None):
        self.name = name
        self.mcp = mcp
        self.manager = manager
        self.parser = argparse.ArgumentParser(description=help_text, prog=name)
        self.subcommands: Dict[str, tuple[argparse.ArgumentParser, Callable]] = {}
        self._setup_commands()

    def _setup_commands(self):
        """Setup the main commands for the CLI."""
        subparsers = self.parser.add_subparsers(
            dest="command", help="Available commands"
        )
        run_parser = subparsers.add_parser(
            "run", help="Start the server with the specified configuration"
        )
        self._setup_run_command(run_parser)
        self.subcommands["run"] = (run_parser, self._run_command)

    def _setup_run_command(self, parser: argparse.ArgumentParser):
        """Setup run command arguments."""
        parser.add_argument(
            "-t",
            "--transport",
            default="stdio",
            choices=["stdio", "shttp", "sse"],
            help="specify transport type",
        )
        parser.add_argument(
            "-p", "--port", type=int, default=8000, help="transport port"
        )
        parser.add_argument("--host", default="127.0.0.1", help="transport host")
        parser.add_argument("-f", "--forward", help="forward request to another server")
        parser.add_argument(
            "-wd", "--working-dir", default=".", help="working directory"
        )
        parser.add_argument(
            "--run-mode", choices=["tool", "code"], default="code", help="run mode"
        )
        parser.add_argument(
            "--tool-mode",
            choices=["auto", "normal"],
            default="normal",
            help="tool selection mode",
        )
        parser.add_argument("--log-file", help="log file path, use stdout if None")

    def add_command(
        self, name: str, help_text: str, handler: Callable
    ) -> argparse.ArgumentParser:
        """add new subcommand

        Args:
            name: subcommand name
            help_text: help text
            handler: handler function

        Returns:
            ArgumentParser: parser for the subcommand
        """
        subparsers = self.parser._subparsers._group_actions[0]
        parser = subparsers.add_parser(name, help=help_text)
        self.subcommands[name] = (parser, handler)
        return parser

    def get_command_parser(self, name: str) -> Optional[argparse.ArgumentParser]:
        """get the parser for the subcommand

        Args:
            name: subcommand name

        Returns:
            ArgumentParser: parser for the subcommand, return None if the subcommand does not exist
        """
        if name in self.subcommands:
            return self.subcommands[name][0]
        return None

    def _run_command(self, args):
        """Start the server with the specified configuration."""
        os.chdir(args.working_dir)
        if hasattr(args, "module"):
            if "all" in args.module:
                modules = None
            elif isinstance(args.module, list) and bool(args.module):
                modules = args.module
        else:
            modules = None
        if self.manager is not None:
            from .backend import NotebookManager, AdataManager

            if args.run_mode == "code":
                backend = NotebookManager
                self.mcp = self.manager(
                    self.name,
                    include_tags=["nb", "rag", "kb", "util"],
                    backend=backend,
                ).mcp
            else:
                backend = AdataManager
                self.mcp = self.manager(
                    self.name,
                    include_modules=modules,
                    backend=backend,
                    exclude_tags=["nb", "rag", "kb", "util"],
                ).mcp
                if args.tool_mode == "auto":
                    for tool in self.mcp._tool_manager._tools:
                        if "auto" not in self.mcp._tool_manager._tools[tool].tags:
                            self.mcp._tool_manager._tools[tool].disable()
                else:
                    for tool in self.mcp._tool_manager._tools:
                        if "auto" in self.mcp._tool_manager._tools[tool].tags:
                            self.mcp._tool_manager._tools[tool].disable()
        elif self.mcp is not None:
            pass
        else:
            raise ValueError("No manager or mcp provided")
        transport = args.transport
        self.run_mcp(args.log_file, args.forward, transport, args.host, args.port)

    def run_mcp(self, log_file, forward, transport, host, port):
        set_env(log_file, forward, transport, host, port)
        from .logging_config import setup_logger

        setup_logger(log_file)
        if transport == "stdio":
            self.mcp.run()
        elif transport in ["sse", "shttp"]:
            transport = "streamable-http" if transport == "shttp" else transport
            add_figure_route(self.mcp)
            self.mcp.run(transport=transport, host=host, port=port, log_level="info")

    def run(self):
        """Run the CLI application."""
        args = self.parser.parse_args()
        if args.command in self.subcommands:
            handler = self.subcommands[args.command][1]
            handler(args)
        else:
            self.parser.print_help()
