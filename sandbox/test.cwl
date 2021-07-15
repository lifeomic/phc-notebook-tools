cwlVersion: v1.0
class: Workflow
hints:
  ResourceRequirement:
    coresMin: 1
    coresMax: 1
    ramMin: 1GB
    ramMax: 1GB
inputs:
  notebook: File
  parameters: File
  output_name: string
outputs:
  executed_notebook:
    type: File
    outputSource: run_notebook/executed_notebook
steps:
  run_notebook:
    in:
      notebook: notebook
      output_name: output_name
      parameters: parameters
    out:
      [executed_notebook]
    run:
      class: CommandLineTool
      hints:
        DockerRequirement:
          dockerPull: notebook-runner
      inputs:
        notebook:
          type: File
          inputBinding:
            position: 1
        output_name:
          type: string
          inputBinding:
            position: 2
        parameters:
          type: File
          inputBinding:
            prefix: -f
            position: 3
      outputs:
        executed_notebook:
          type: File
          outputBinding:
            glob: '$(inputs.output_name)'