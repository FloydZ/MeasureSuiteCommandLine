{ pkgs ? import <nixpkgs> {} }:
let
  my-python = pkgs.python3;
  python-with-my-packages = my-python.withPackages (p: with p; [
	pycparser
  ]);
in
pkgs.mkShell {
  buildInputs = [
    pkgs.clang
    pkgs.gcc
    pkgs.calc   # needed for `msc` and `ms`
    pkgs.jq     # needed for `msc` and `ms`
    pkgs.pkg-config # needed to compile `MeasureSuite` with `AssemblyLine`
    python-with-my-packages
  ];

  # postShellHook = ''
  #   # python
  #   export PYTHONPATH=${python-with-my-packages}/${python-with-my-packages.sitePackages}
  # '';

  shellHook = ''
    ./build.sh
  '';
}
