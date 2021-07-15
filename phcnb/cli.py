from typing import Any, List, Mapping, TypedDict
import click
import papermill as pm
from yaml import dump
import os


class Parameter(TypedDict):
    name: str
    inferred_type_name: str
    default: str
    help: str

@click.group()
def cli():
    pass

def create_input(parameter: Parameter):
    #TODO: handle inferred types rather than just treating params as a string
    result = {
        'type': 'File' if parameter['help'] == 'input file' else 'string'
    }
    if parameter['help']:
        result['doc'] = parameter['help']
    if parameter['default']:
        value = parameter['default'].strip("'")
        result['default'] = f'"{value}"'

    return result

@cli.command()
@click.argument("notebook", required=True)
def workflow(notebook):
    parameters: Mapping[str, Parameter] = pm.inspect_notebook(notebook)

    # TODO: upload notebook to TRS
    notebook_tool = 'lifeomic_tool/my_notebook'

    inputs: Mapping[str, Any] = {
        'notebook_out_name': {
            'type': 'String',
            'doc': 'file name for the output notebook',
            'default': 'output.ipynb'
        }
    }
    outputs: Mapping[str, Any] = {
        'notebook_out': {
            'type': 'File',
            'outputSource': 'run_notebook/notebook_out'
        }
    }
    step_in: Mapping[str, Any] = {
        'notebook_out_name': 'notebook_out_name'
    }
    step_out: List[str] = ['notebook_out']
    step_inputs: Mapping[str, Any] = {
        'NOTEBOOK': {
            'type': 'string',
            'default': notebook_tool,
            'inputBinding': {
                'position': 1
            }
        },
        'notebook_out_name': {
            'type': 'String',
            'inputBinding': {
                'position': 2
            }
        }
    }
    step_outputs: Mapping[str, Any] = {
        'notebook_out': {
            'type': 'File',
            'outputBinding': {
                'glob': '$(inputs.notebook_out_name)'
            }
        }
    }

    for name, parameter in parameters.items():
        if parameter['help'] == 'input file':
            inputs[name] = create_input(parameter)
            step_in[name] = name
            step_inputs[name] = {
                'type': 'File',
                'inputBinding': {
                    'prefix': f'-p {name}',
                    'position': 3
                }
            }

        elif parameter['help'] == 'output file':
            step_outputs[name] = {
                'type': 'File',
                'outputBinding': {
                   'glob': parameter['default']
                }
            }
            step_out.append(name)
            pass
        else:
            inputs[name] = create_input(parameter)
            step_in[name] = name
            step_inputs[name] = {
                'type': 'string',
                'inputBinding': {
                    'prefix': f'-p {name}',
                    'position': 3
                }
            }

    workflow = {
        'cwlVersion': 'v1.0',
        'class': 'Workflow',
        'hints': {
            'ResourceRequirement': {
                'coresMin': 2,
                'coresMax': 4,
                'ramMin': '8GB',
                'ramMax': '16GB'
            }
        },
        'inputs': inputs,
        'outputs': outputs,
        'steps': {
            'run_notebook': {
                'in': step_in,
                'out': step_out,
                'run': {
                    'class': 'CommandLineTool',
                    'hints': {
                        'DockerRequirement': {
                            'dockerPull': 'lifeomic_tool/notebook-runner'
                        }
                    },
                    'inputs': step_inputs,
                    'outputs': step_outputs
                }
            }
        }
    }

    print(dump(workflow))
