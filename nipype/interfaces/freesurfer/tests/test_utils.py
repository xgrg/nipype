# -*- coding: utf-8 -*-
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
from __future__ import print_function, division, unicode_literals, absolute_import
from builtins import open

import os
from tempfile import mkdtemp
from shutil import rmtree

import numpy as np

import nibabel as nif
import pytest
from nipype.interfaces.base import TraitError

import nipype.interfaces.freesurfer as fs


@pytest.fixture()
def create_files_in_directory(request):
    outdir = os.path.realpath(mkdtemp())
    cwd = os.getcwd()
    os.chdir(outdir)
    filelist = ['a.nii', 'b.nii']
    for f in filelist:
        hdr = nif.Nifti1Header()
        shape = (3, 3, 3, 4)
        hdr.set_data_shape(shape)
        img = np.random.random(shape)
        nif.save(nif.Nifti1Image(img, np.eye(4), hdr),
                 os.path.join(outdir, f))
    with open(os.path.join(outdir, 'reg.dat'), 'wt') as fp:
        fp.write('dummy file')
    filelist.append('reg.dat')

    def clean_directory():
        if os.path.exists(outdir):
            rmtree(outdir)
        os.chdir(cwd)

    request.addfinalizer(clean_directory)
    return (filelist, outdir, cwd)


@pytest.fixture()
def create_surf_file(request):
    outdir = os.path.realpath(mkdtemp())
    cwd = os.getcwd()
    os.chdir(outdir)
    surf = 'lh.a.nii'
    hdr = nif.Nifti1Header()
    shape = (1, 100, 1)
    hdr.set_data_shape(shape)
    img = np.random.random(shape)
    nif.save(nif.Nifti1Image(img, np.eye(4), hdr),
             os.path.join(outdir, surf))

    def clean_directory():
        if os.path.exists(outdir):
            rmtree(outdir)
        os.chdir(cwd)

    request.addfinalizer(clean_directory)
    return (surf, outdir, cwd)


@pytest.mark.skipif(fs.no_freesurfer(), reason="freesurfer is not installed")
def test_sample2surf(create_files_in_directory):

    s2s = fs.SampleToSurface()
    # Test underlying command
    assert s2s.cmd == 'mri_vol2surf'

    # Test mandatory args exception
    with pytest.raises(ValueError): s2s.run()

    # Create testing files
    files, cwd, oldwd = create_files_in_directory

    # Test input settings
    s2s.inputs.source_file = files[0]
    s2s.inputs.reference_file = files[1]
    s2s.inputs.hemi = "lh"
    s2s.inputs.reg_file = files[2]
    s2s.inputs.sampling_range = .5
    s2s.inputs.sampling_units = "frac"
    s2s.inputs.sampling_method = "point"

    # Test a basic command line
    assert s2s.cmdline == ("mri_vol2surf "
                           "--hemi lh --o %s --ref %s --reg reg.dat --projfrac 0.500 --mov %s"
                           % (os.path.join(cwd, "lh.a.mgz"), files[1], files[0]))

    # Test identity
    s2sish = fs.SampleToSurface(source_file=files[1], reference_file=files[0], hemi="rh")
    assert s2s != s2sish

    # Test hits file name creation
    s2s.inputs.hits_file = True
    assert s2s._get_outfilename("hits_file") == os.path.join(cwd, "lh.a_hits.mgz")

    # Test that a 2-tuple range raises an error
    def set_illegal_range():
        s2s.inputs.sampling_range = (.2, .5)
    with pytest.raises(TraitError): set_illegal_range()


@pytest.mark.skipif(fs.no_freesurfer(), reason="freesurfer is not installed")
def test_surfsmooth(create_surf_file):

    smooth = fs.SurfaceSmooth()

    # Test underlying command
    assert smooth.cmd == "mri_surf2surf"

    # Test mandatory args exception
    with pytest.raises(ValueError): smooth.run()

    # Create testing files
    surf, cwd, oldwd = create_surf_file

    # Test input settings
    smooth.inputs.in_file = surf
    smooth.inputs.subject_id = "fsaverage"
    fwhm = 5
    smooth.inputs.fwhm = fwhm
    smooth.inputs.hemi = "lh"

    # Test the command line
    assert smooth.cmdline == \
        ("mri_surf2surf --cortex --fwhm 5.0000 --hemi lh --sval %s --tval %s/lh.a_smooth%d.nii --s fsaverage" %
         (surf, cwd, fwhm))

    # Test identity
    shmooth = fs.SurfaceSmooth(
        subject_id="fsaverage", fwhm=6, in_file=surf, hemi="lh", out_file="lh.a_smooth.nii")
    assert smooth != shmooth


@pytest.mark.skipif(fs.no_freesurfer(), reason="freesurfer is not installed")
def test_surfxfm(create_surf_file):

    xfm = fs.SurfaceTransform()

    # Test underlying command
    assert xfm.cmd == "mri_surf2surf"

    # Test mandatory args exception
    with pytest.raises(ValueError): xfm.run()

    # Create testing files
    surf, cwd, oldwd = create_surf_file

    # Test input settings
    xfm.inputs.source_file = surf
    xfm.inputs.source_subject = "my_subject"
    xfm.inputs.target_subject = "fsaverage"
    xfm.inputs.hemi = "lh"

    # Test the command line
    assert xfm.cmdline == \
        ("mri_surf2surf --hemi lh --tval %s/lh.a.fsaverage.nii --sval %s --srcsubject my_subject --trgsubject fsaverage" %
         (cwd, surf))

    # Test identity
    xfmish = fs.SurfaceTransform(
        source_subject="fsaverage", target_subject="my_subject", source_file=surf, hemi="lh")
    assert xfm != xfmish


@pytest.mark.skipif(fs.no_freesurfer(), reason="freesurfer is not installed")
def test_surfshots(create_files_in_directory):

    fotos = fs.SurfaceSnapshots()

    # Test underlying command
    assert fotos.cmd == "tksurfer"

    # Test mandatory args exception
    with pytest.raises(ValueError): fotos.run()

    # Create testing files
    files, cwd, oldwd = create_files_in_directory

    # Test input settins
    fotos.inputs.subject_id = "fsaverage"
    fotos.inputs.hemi = "lh"
    fotos.inputs.surface = "pial"

    # Test a basic command line
    assert fotos.cmdline == "tksurfer fsaverage lh pial -tcl snapshots.tcl"

    # Test identity
    schmotos = fs.SurfaceSnapshots(subject_id="mysubject", hemi="rh", surface="white")
    assert fotos != schmotos

    # Test that the tcl script gets written
    fotos._write_tcl_script()
    assert os.path.exists("snapshots.tcl")

    # Test that we can use a different tcl script
    foo = open("other.tcl", "w").close()
    fotos.inputs.tcl_script = "other.tcl"
    assert fotos.cmdline == "tksurfer fsaverage lh pial -tcl other.tcl"

    # Test that the interface crashes politely if graphics aren't enabled
    try:
        hold_display = os.environ["DISPLAY"]
        del os.environ["DISPLAY"]
        with pytest.raises(RuntimeError): fotos.run()
        os.environ["DISPLAY"] = hold_display
    except KeyError:
        pass
