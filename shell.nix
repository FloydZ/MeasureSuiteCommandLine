{ pkgs ? import <nixpkgs> {} }:
let
  myPython = pkgs.python311;
  pythonPackages = pkgs.python311Packages;
  pythonWithPkgs = myPython.withPackages (pythonPkgs: with pythonPkgs; [
    ipython
    pip
    setuptools
    virtualenv
    wheel
  ]);

  # add the needed packages here
  extraBuildInputs = with pkgs; [
    myPython
    pythonPackages.numpy
    pythonPackages.pytest
    pythonPackages.pylint
    pythonPackages.pycparser
    pythonPackages.sphinx


    # needed to compile `MeasureSuite` with `AssemblyLine`
    pkg-config 
    automake
    autoconf
    libtool
    nasm      # needed for testing
    clang
    gcc
    calc   # needed for `msc` and `ms`
    jq     # needed for `msc` and `ms`

    # dev
    ruff
    jetbrains.pycharm-community
  ] ++ (lib.optionals pkgs.stdenv.isLinux ([
  ]));
in
let
  buildInputs  = with pkgs; [
      clang
      llvmPackages.bintools
      rustup
  ] ++ extraBuildInputs;
  lib-path = with pkgs; lib.makeLibraryPath buildInputs;
  shell = pkgs.mkShell {
    buildInputs = [
       # my python and packages
        pythonWithPkgs
        
        # other packages needed for compiling python libs
        pkgs.readline
        pkgs.libffi
        pkgs.openssl
        pkgs.clang
  
        # unfortunately needed because of messing with LD_LIBRARY_PATH below
        pkgs.git
        pkgs.openssh
        pkgs.rsync
    ] ++ extraBuildInputs;
    shellHook = ''
        # Allow the use of wheels.
        SOURCE_DATE_EPOCH=$(date +%s)
        # Augment the dynamic linker path
        export "LD_LIBRARY_PATH=$LD_LIBRARY_PATH:${lib-path}"
        # Setup the virtual environment if it doesn't already exist.
        VENV=.venv
        if test ! -d $VENV; then
          virtualenv $VENV
        fi
        source ./$VENV/bin/activate
        export PYTHONPATH=$PYTHONPATH:`pwd`/$VENV/${myPython.sitePackages}/
        ./build.sh
        pip install -e .
    '';
  };
in shell
