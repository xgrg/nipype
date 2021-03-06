# AUTO-GENERATED by tools/checkspecs.py - DO NOT EDIT
from ..preprocess import SegmentWM


def test_SegmentWM_inputs():
    input_map = dict(args=dict(argstr='%s',
    ),
    environ=dict(nohash=True,
    usedefault=True,
    ),
    ignore_exception=dict(nohash=True,
    usedefault=True,
    ),
    in_file=dict(argstr='%s',
    mandatory=True,
    position=-2,
    ),
    out_file=dict(argstr='%s',
    mandatory=True,
    position=-1,
    ),
    subjects_dir=dict(),
    terminal_output=dict(nohash=True,
    ),
    )
    inputs = SegmentWM.input_spec()

    for key, metadata in list(input_map.items()):
        for metakey, value in list(metadata.items()):
            assert getattr(inputs.traits()[key], metakey) == value


def test_SegmentWM_outputs():
    output_map = dict(out_file=dict(),
    )
    outputs = SegmentWM.output_spec()

    for key, metadata in list(output_map.items()):
        for metakey, value in list(metadata.items()):
            assert getattr(outputs.traits()[key], metakey) == value
