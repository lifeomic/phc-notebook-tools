from typing import Any, List, Mapping, TypedDict
import click
import papermill as pm
from yaml import dump
import os

IMAGE_NAME = 'notebook-runner'
INPUT_FILE = 'input file'
OUTPUT_FILE = 'output file'

class Parameter(TypedDict):
    name: str
    inferred_type_name: str
    default: str
    help: str

@click.group()
def cli():
    pass

def is_param_a_file(parameter: Parameter):
    return 'help' in parameter and (parameter['help'] == INPUT_FILE or parameter['help'] == OUTPUT_FILE)

def cwl_type_from_param(parameter: Parameter):
    if is_param_a_file(parameter):
        return 'File'
    elif 'inferred_type_name' not in parameter:
        return 'string'
    elif parameter['inferred_type_name'] == 'int':
        return 'long'
    elif parameter['inferred_type_name'] == 'float':
        return 'double'
    elif parameter['inferred_type_name'] == 'bool':
        return 'boolean'
    else:
        return 'string'

def cwl_default_from_param(parameter: Parameter):
    if is_param_a_file(parameter):
        return None
    elif 'inferred_type_name' not in parameter:
        return parameter['default'].strip('\'"')
    elif parameter['inferred_type_name'] == 'int':
        return int(parameter['default'])
    elif parameter['inferred_type_name'] == 'float':
        return float(parameter['default'])
    elif parameter['inferred_type_name'] == 'bool':
        return bool(parameter['default'])
    else:
        return parameter['default'].strip('\'"')

def create_input_from_param(parameter: Parameter):
    result = {
        'type': cwl_type_from_param(parameter)
    }

    default = cwl_default_from_param(parameter)

    if default is not None:
        result['default'] =  default

    if parameter['help']:
        result['doc'] = parameter['help']

    return result

@cli.command()
@click.argument("notebook", required=True)
def workflow(notebook):
    parameters: Mapping[str, Parameter] = pm.inspect_notebook(notebook)

    with open(notebook) as f:
        notebook_contents = f.read()

    arguments = [notebook]
    inputs: Mapping[str, Any] = {
        'notebook_out_name': {
            'type': 'string',
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
        'notebook_out_name': {
            'type': 'string',
            'inputBinding': {
                'position': 1
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

    num_inputs = 0
    for name, parameter in parameters.items():
        if parameter['help'] == INPUT_FILE:
            inputs[name] = create_input_from_param(parameter)
            step_in[name] = name
            arguments.append({
                'valueFrom': '-p',
                'position': num_inputs*3 + 2
            })
            arguments.append({
                'valueFrom': name,
                'position': num_inputs*3 + 3
            })
            step_inputs[name] = {
                'type': 'File',
                'inputBinding': {
                    'position': num_inputs*3 + 4
                }
            }
            num_inputs += 1

        elif parameter['help'] == OUTPUT_FILE:
            outputs[parameter['name']] = {
                'outputSource': f"run_notebook/{parameter['name']}",
                'type': 'File'
            }
            step_outputs[name] = {
                'type': 'File',
                'outputBinding': {
                   'glob': parameter['default'].strip('\'"')
                }
            }
            step_out.append(name)
            pass

        else:
            inputs[name] = create_input_from_param(parameter)
            step_in[name] = name
            arguments.append({
                'valueFrom': '-p',
                'position': num_inputs*3 + 2
            })
            arguments.append({
                'valueFrom': name,
                'position': num_inputs*3 + 3
            })
            step_inputs[name] = {
                'type': cwl_type_from_param(parameter),
                'inputBinding': {
                    'position': num_inputs*3 + 4
                }
            }
            num_inputs += 1

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
                            'dockerPull': IMAGE_NAME
                        }
                    },
                    'requirements': {
                        'InitialWorkDirRequirement': {
                            'listing': [
                                {
                                    'entryname': notebook,
                                    'entry': notebook_contents.replace('$', r'\$')
                                }
                            ]
                        }
                    },
                    'arguments': arguments,
                    'inputs': step_inputs,
                    'outputs': step_outputs
                }
            }
        }
    }

    print(dump(workflow))
