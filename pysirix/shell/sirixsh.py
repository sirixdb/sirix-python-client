from .. import DBType, Insert, sirix_sync, SirixServerError
import httpx

import json
import cmd
import argparse
import shlex
from datetime import datetime
import getpass
from pathlib import Path

from xml.etree import ElementTree as ET


def delete_parser():
    parser = argparse.ArgumentParser(
        description=f"Delete server/database/resource/node", prog="delete",
    )

    macro_group = parser.add_mutually_exclusive_group()
    macro_group.add_argument(
        "-s",
        "--server",
        action="store_true",
        help="delete all databases and their resources",
    )
    macro_group.add_argument(
        "-d",
        "--database",
        action="store_true",
        help="delete the entire database in current context",
    )
    macro_group.add_argument(
        "-r",
        "--resource",
        action="store_true",
        help="delete the entire resource in current context",
    )

    node_group = parser.add_argument_group()
    node_group.add_argument(
        "-n", "--nodekey", type=int, help="nodekey of node to delete."
    )
    node_group.add_argument("-e", "--etag", help="hash of node to delete. Optional.")
    return parser


def read_parser():
    parser = argparse.ArgumentParser(description="Read from the resource.", prog="read")
    parser.add_argument(
        "-n",
        "--nodekey",
        type=int,
        help="the nodekey to read from the resource. Defaults to root.",
    )
    parser.add_argument(
        "-r",
        "--revision",
        help="Revision number, or timestamp, to read from. Defaults to latest. For multiple revisions, see --revision-start",
    )
    parser.add_argument(
        "-s",
        "--start-revision",
        help="Revision number, or timestamp, to begin reading from.",
    )
    parser.add_argument(
        "-e",
        "--end-revision",
        help="Revision number, or timestamp, to read from last.",
    )
    parser.add_argument(
        "-d",
        "--max-depth",
        type=int,
        default=None,
        help="The maximum depth to read to. Defaults to maximum.",
    )
    parser.add_argument(
        "-m",
        "--metadata",
        type=bool,
        default=False,
        help="Whether to read with metadata of each node. Defaults to False.",
    )
    return parser


def diff_parser():
    parser = argparse.ArgumentParser(description="Read from the resource.", prog="diff")
    parser.add_argument(
        "-s",
        "--start-revision",
        required=True,
        help="Revision number, or timestamp, to begin reading from.",
    )
    parser.add_argument(
        "-e",
        "--end-revision",
        required=True,
        help="Revision number, or timestamp, to read from last.",
    )
    parser.add_argument(
        "-n",
        "--nodekey",
        type=int,
        help="the nodekey to read from the resource. Defaults to root.",
    )
    parser.add_argument(
        "-d",
        "--max-depth",
        type=int,
        default=None,
        help="The maximum depth to read to. Defaults to maximum.",
    )
    return parser


def update_parser():
    parser = argparse.ArgumentParser(
        description=f"Delete server/database/resource/node", prog="update",
    )
    parser.add_argument(
        "-n", "--nodekey", required=True, type=int, help="nodekey of node to delete.",
    )
    parser.add_argument("-e", "--etag", help="hash of node to delete. Optional.")
    data_group = parser.add_mutually_exclusive_group(required=True)
    data_group.add_argument("-d", "--data", help="the data to insert.")
    data_group.add_argument("-p", "--data-path", help="the path to data to insert.")
    parser.add_argument(
        "-i",
        "--insert",
        help="the position to insert the data in, relative to the nodekey. "
        "options (case insensitive) are CHILD, LEFT, RIGHT, REPLACE. defaults to CHILD.",
    )
    return parser


def rquery_parser():
    parser = argparse.ArgumentParser(description="Read from the resource.", prog="diff")
    parser.add_argument(
        "-s", "--start-index", help="Start result index, for pagination.",
    )
    parser.add_argument(
        "-e", "--end-revision", help="End result index, for pagination.",
    )
    parser.add_argument(
        "-q", "--query", required=True, help="the query to execute on the resource.",
    )
    return parser


def query_parser():
    parser = argparse.ArgumentParser(
        description="Execute an unbound custom query context of the server.",
        prog="diff",
    )
    parser.add_argument(
        "-s", "--start-index", help="Start result index, for pagination.",
    )
    parser.add_argument(
        "-e", "--end-revision", help="End result index, for pagination.",
    )
    parser.add_argument(
        "-q", "--query", required=True, help="the query to execute on the resource.",
    )
    return parser


def parse_revision(revision: str):
    try:
        return int(revision)
    except ValueError:
        pass
    try:
        return datetime.strptime(revision, "%Y-%m-%d")
    except ValueError:
        pass
    try:
        return datetime.strptime(revision, "%Y-%m-%dT%H:%M")
    except ValueError:
        pass
    try:
        return datetime.strptime(revision, "%Y-%m-%d %H:%M")
    except ValueError:
        pass
    try:
        return datetime.strptime(revision, "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        pass
    try:
        return datetime.strptime(revision, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        pass
    try:
        return datetime.strptime(revision, "%Y-%m-%dT%H:%M:%S.%f")
    except ValueError:
        pass
    try:
        return datetime.strptime(revision, "%Y-%m-%d %H:%M:%S.%f")
    except ValueError:
        pass
    return None


profile = "empty"


def get_config():
    try:
        home = str(Path.home())
        with open(f"{home}/pysirix-shell/config.json") as f:
            config = json.load(f)
    except FileNotFoundError:
        config = {}
    print("profiles:")
    for k, v in config.items():
        print(json.dumps({k: v}, indent=2))
    print()
    if len(config) == 1:
        selected = next(iter(config))
        print(f"Selecting profile '{selected}'")
    else:
        while True:
            selected = input("please enter your profile: ")
            if selected in config:
                break
    print()
    global profile
    profile = selected
    return dict(**config[selected])


class SirixShell(cmd.Cmd):
    prompt = "PySirix> "

    def preloop(self):
        sirix_uri = config.get("url")
        cert_path = config.get("cert")
        username = config.get("username")
        timeout = config.get("timeout", 5)

        if cert_path is None:
            cert_path = True
        if sirix_uri is None:
            sirix_uri = "https://localhost:9443"
        if username is None:
            username = input(
                "This profile does not have a username set. Enter your username: "
            )
        password = getpass.getpass("enter your password: ")

        self.client = httpx.Client(
            base_url=sirix_uri, verify=cert_path, timeout=timeout
        )
        self.sirix = sirix_sync(username, password, self.client)
        self.context = {"root": profile}
        self.file = None

    def emptyline(self):
        pass

    def do_repeat(self, args):
        """
        Execute the last command entered again.
        """
        super().emptyline()

    def do_last(self, args):
        """
        Print the last result returned by the shell.
        """
        try:
            print(self.last_result)
        except AttributeError:
            print("No results cached yet.")

    def postcmd(self, stop, line):
        print("")
        return super().postcmd(stop, line)

        # ----- record and playback -----

    def do_record(self, arg):
        """
        Save future commands to filename: record <filename>.
        Terminate recording with `record stop`.
        """
        if arg == "stop":
            self._close()
        else:
            home = str(Path.home())
            self.file = open(f"{home}/pysirix-shell/{arg}", "w")

    def do_run(self, arg):
        """
        Run commands from a file:  playback <filename>.
        """
        self._close()
        try:
            home = str(Path.home())
            with open(f"{home}/pysirix-shell/{arg}") as f:
                for command in f:
                    print(f"> {command}")
                    self.cmdqueue.append(command)
        except FileNotFoundError as e:
            print(e)

    def precmd(self, line: str):
        line = line.lower()
        if (
            self.file
            and not line.startswith("playback")
            and not line.startswith("record stop")
        ):
            print(line, file=self.file)
        return line

    def _close(self):
        if self.file:
            self.file.close()
            self.file = None

        # ----- end record and playback -----

    def do_root(self, args):
        """
        Change context to root of sirix server.
        """
        if self.context.get("database"):
            del self.context["database"]
        if self.context.get("resource"):
            del self.context["resource"]
        self.prompt = "PySirix> "

    def do_database(self, args: str):
        """
        Change context to database of <name> and <type>.
        USAGE: "database <name> <type>".
        """
        try:
            name, db_type = shlex.split(args)
        except ValueError:
            print('Error: You must provide two arguments. "<name> <type>".')
            return
        self._database_context(name, db_type)

    def _database_context(self, name: str, database_type: str):
        if database_type.lower() in ["json", "xml"]:
            db_type: DBType = DBType.JSON if database_type.lower() == "json" else DBType.XML
            self.database = self.sirix.database(name, db_type)
            self.context["database"] = (name, db_type)
            if self.context.get("resource"):
                del self.context["resource"]
            self.prompt = f"{self.context['root']}/{name} ({database_type.upper()})> "
        else:
            print(
                'Error: Invalid database type. valid types are "JSON" and "XML" (case insensitive)'
            )

    def do_resource(self, args: str):
        """
        Change context context to resource of <name>.
        USAGE: "resource <name>". Or "resource <db_name> <type> <name>".
        """
        args = shlex.split(args)
        if len(args) == 3:
            self._database_context(args[0], args[1])
            name = args[2]
        elif len(args) != 1:
            print("You must provide 1 or 3 arguments.")
            return
        else:
            name = args[0]
        self._resource_context(name)

    def _resource_context(self, name: str):
        self.resource = self.database.resource(name)
        self.context["resource"] = name
        db_name, db_type = self.context["database"]
        show_type = "JSON" if db_type == DBType.JSON else "XML"
        self.prompt = f"{self.context['root']}/{db_name}/{name} ({show_type})> "

    def do_info(self, args):
        """
        Retrieve information about the servers databases and resources, or
        about the resources of the database in current context. Type `info help`
        for more information.
        """
        if self.context.get("database"):
            try:
                result = self.database.get_database_info()
            except SirixServerError as e:
                print(e)
                return
        else:
            resources = True
            if args in ["none", "false", "no-resources"]:
                resources = False
            try:
                result = self.sirix.get_info(resources)
            except SirixServerError as e:
                print(e)
                return
        print(json.dumps(result, indent=2))
        self.last_result = result

    def do_exists(self, args):
        """
        Returns the existence of the resource in current context.
        """
        if self.context.get("resource"):
            try:
                result = self.resource.exists()
                print(f"exists: {result}")
                self.last_result = result
            except SirixServerError as e:
                print(e)
        else:
            print("Error: Not in context of resource.")

    def do_create(self, args: str):
        """
        Create a database or resource, depending on current context. Type `create help` for more information.
        """
        if self.context.get("resource"):
            parser = argparse.ArgumentParser(
                description=f"Create resource <{self.context['resource']}>",
                prog="create",
            )
            group = parser.add_mutually_exclusive_group(required=True)
            group.add_argument("-p", "--data-path")
            group.add_argument(
                "-d", "--data",
            )
            try:
                parsed = vars(parser.parse_args(shlex.split(args)))
            except:
                return
            if parsed.get("data"):
                data = parsed["data"]
            else:
                with open(parsed["data_path"]) as f:
                    data = f.read()
            try:
                self.resource.create(data)
            except SirixServerError as e:
                print(e)
                return
            print(f"created resource {self.context['resource']}")
        elif self.context.get("database"):
            try:
                self.database.create()
            except SirixServerError as e:
                print(e)
                return
            print(f"created database {self.context['database'][0]}")
        else:
            print("Error: Not in context of database or resource.")

    def do_delete(self, args: str):
        """
        Delete everything on the server, or the database in current context,
        or the resource in current context, or a particular node in the resource
        in current context. Type `delete help` for more information.
        """
        parser = delete_parser()
        try:
            parsed = vars(parser.parse_args(args.split()))
        except:
            return
        try:
            db_name, db_type = self.context.get("database")
        except TypeError:
            db_name, db_type = None, None
        show_type = (
            "JSON"
            if db_type == DBType.JSON
            else "XML"
            if db_type == DBType.XML
            else None
        )
        if parsed.get("nodekey") is not None:
            nodeKey = parsed["nodekey"]
            etag = parsed.get("etag")
            try:
                self.resource.delete(nodeKey, etag)
            except SirixServerError as e:
                print(e)
                return
            print(f"Node with nodeKey: {nodeKey} deleted")
        elif parsed.get("resource"):
            if self.context.get("resource"):
                try:
                    self.resource.delete(None, None)
                except SirixServerError as e:
                    print(e)
                    return
                print(
                    " ".join(
                        [
                            "Deleted resource",
                            f"<{self.context['resource']}>",
                            f"of database <{db_name}> of type <{show_type}>",
                        ]
                    )
                )
            else:
                print("Error: Not in the context of a resource.")
        elif parsed.get("database"):
            if db_name is not None:
                try:
                    self.database.delete()
                    print(f"Deleted database <{db_name}> of type <{show_type}>.")
                except SirixServerError as e:
                    print(e)
            else:
                print("Error: Not in the context of a database.")
        elif parsed.get("server"):
            try:
                self.sirix.delete_all()
                print("Deleted all databases and resources.")
            except SirixServerError as e:
                print(e)
        else:
            print("Error: invalid delete specification")

    def do_read(self, args):
        """
        Read from the resource in current context. Type `read help` for more information.
        """
        if not self.context.get("resource"):
            print("Error: Not in the context of a resource.")
            return
        parser = read_parser()
        try:
            parsed = vars(parser.parse_args(shlex.split(args)))
        except:
            return
        node_key = parsed.get("nodekey")
        max_level = parsed.get("max_depth")
        revision = parsed.get("revision")
        start_revision = parsed.get("start_revision")
        end_revision = parsed.get("end_revision")
        rev = None
        if start_revision is not None:
            start_rev = parse_revision(start_revision)
            if start_rev is None:
                print(f"Error: {start_revision} is of invalid form.")
                return
            end_rev = parse_revision(end_revision)
            if end_rev is None:
                print(f"Error: {end_revision} is of invalid form.")
                return
            rev = (start_rev, end_rev)
        if revision is not None:
            rev = parse_revision(revision)
            if rev is None:
                print(f"Error: {revision} is of invalid form.")
                return
        try:
            if parsed.get("metadata"):
                result = self.resource.read_with_metadata(node_key, rev, max_level=max_level)
            else:
                result = self.resource.read(node_key, rev, max_level)
            if self.context["database"][1] == DBType.JSON:
                print(json.dumps(result, indent=2))
            else:
                result = ET.tostring(result, encoding="unicode").replace("\\n", "\n")
                print(result)
            self.last_result = result
        except SirixServerError as e:
            print(e)

    def do_history(self, args: str):
        """
        Retrieve history of resource in current context.
        """
        if self.context.get("resource") is None:
            print("Not in the context of a resource.")
            return
        try:
            result = self.resource.history()
            print(json.dumps(result, indent=2))
            self.last_result = result
        except SirixServerError as e:
            print(e)

    def do_hash(self, args):
        """
        Retrieve hash of the node corresponding to <nodekey> in the resource in current context.
        USAGE: hash <nodekey>
        """
        if self.context.get("resource"):
            try:
                node_id = int(args)
            except ValueError:
                print("Error: Invalid nodekey.")
                return
            try:
                result = self.resource.get_etag(node_id)
                self.last_result = result
                print(result)
            except SirixServerError as e:
                print(e)
        else:
            print("Error: Not in the context of a resource.")

    def do_diff(self, args):
        """
        Return the differential between two revision of the resource in
        current context. Type `diff help` for more information.
        """
        if self.context.get("resource") is None:
            print("Not in the context of a resource.")
            return
        parser = diff_parser()
        try:
            parsed = vars(parser.parse_args(shlex.split(args)))
        except:
            return
        start_revision = parsed["start_revision"]
        end_revision = parsed["end_revision"]
        nodekey = parsed.get("nodekey")
        depth = parsed.get("max_depth")
        start_rev = None
        end_rev = None
        start_rev = parse_revision(start_revision)
        if start_rev is None:
            print(f"Error: {start_revision} is of invalid form.")
        end_rev = parse_revision(end_revision)
        if end_rev is None:
            print(f"Error: {end_revision} is of invalid form.")
        try:
            result = self.resource.diff(start_rev, end_rev, nodekey, depth)
            print(json.dumps(result, indent=2))
            self.last_result = result
        except SirixServerError as e:
            print(e)

    def do_update(self, args):
        """
        Update the data in the resource in current context. Type `update help`
        for more information.
        """
        if self.context.get("resource") is None:
            print("Not in the context of a resource.")
            return
        parser = update_parser()
        try:
            parsed = vars(parser.parse_args(shlex.split(args)))
        except:
            return
        nodekey = parsed["nodekey"]
        data = parsed.get("data")
        if data is None:
            with open(parsed["data_path"]) as f:
                data = f.read()
        etag = parsed.get("etag")
        insert = parsed.get("insert")
        if insert is None:
            insert = Insert.CHILD
        else:
            insert = Insert[insert.upper()]
        try:
            self.resource.update(nodekey, data, insert, etag)
        except SirixServerError as e:
            print(e)

    def do_rquery(self, args):
        """
        Execute custom query on a resource. Type `rquery help` for more information.
        """
        parser = rquery_parser()
        try:
            parsed = vars(parser.parse_args(shlex.split(args)))
        except:
            return
        try:
            result = self.resource.query(
                parsed["query"], parsed.get("start_index"), parsed.get("end_index")
            )
            if self.context["database"][1] == DBType.JSON:
                print(json.dumps(result, indent=2))
            else:
                result = ET.tostring(result, encoding="unicode").replace("\\n", "\n")
                print(result)
            self.last_result = result
        except SirixServerError as e:
            print(e)

    def do_query(self, args):
        parser = query_parser()
        try:
            parsed = vars(parser.parse_args(shlex.split(args)))
        except:
            return
        try:
            print(parsed)
            print()
            result = self.sirix.query(
                parsed["query"], parsed.get("start_index"), parsed.get("end_index")
            )
            if self.context["database"][1] == DBType.JSON:
                print(json.dumps(result, indent=2))
            else:
                result = ET.tostring(result, encoding="unicode").replace("\\n", "\n")
                print(result)
            self.last_result = result
        except SirixServerError as e:
            print(e)


def main():
    global config
    config = get_config()
    shell = SirixShell()
    try:
        shell.cmdloop()
    except BaseException as e:
        print(e)
        shell.client.close()
        exit()
