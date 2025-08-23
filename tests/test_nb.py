import pytest
from fastmcp import Client
import nest_asyncio

nest_asyncio.apply()


@pytest.mark.asyncio
async def test_notebook(nb_mcp_fixture):
    async with Client(nb_mcp_fixture) as client:
        # Test create_notebook
        result = await client.call_tool(
            "nb_create_notebook", {"nbid": "test", "kernel": "python3"}
        )
        assert "test" in result.content[0].text

        # Test switch_active_notebook
        result = await client.call_tool("nb_switch_active_notebook", {"nbid": "test"})
        assert "switched to notebook test" in result.content[0].text

        # Test single_step_execute (mock code)
        result = await client.call_tool(
            "nb_single_step_execute",
            {"code": "print('hello')", "backup_var": None, "show_var": None},
        )
        assert "hello" in result.content[0].text

        # Test single_step_execute show_var
        result = await client.call_tool(
            "nb_single_step_execute",
            {"code": "hello = 'hello2'", "backup_var": None, "show_var": "hello"},
        )
        assert "hello2" in result.content[0].text

        # Test single_step_execute show_var
        result = await client.call_tool(
            "nb_single_step_execute",
            {"code": "hello = 'hello3'\nprint(hello)", "backup_var": ["hello"]},
        )
        assert "hello3" in result.content[0].text

        # Test multi_step_execute (mock code)
        result = await client.call_tool(
            "nb_multi_step_execute",
            {"code": "a = 123\nprint(a)", "backup_var": None, "show_var": None},
        )
        assert "123" in result.content[0].text

        # Test query_api_doc (mock code)
        result = await client.call_tool(
            "nb_query_api_doc", {"code": "import math\nmath.sqrt.__doc__"}
        )
        assert "square root" in result.content[0].text

        # Test list_notebooks
        result = await client.call_tool("nb_list_notebooks")
        assert "test" in result.content[0].text

        # Test shutdown_notebook
        result = await client.call_tool("nb_kill_notebook", {"nbid": "test"})
        print(result.content[0].text)
        assert "Notebook test shutdown" in result.content[0].text
