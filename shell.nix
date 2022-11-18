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
    python-with-my-packages
  ];

  shellHook = ''
	# python
	PYTHONPATH=${python-with-my-packages}/${python-with-my-packages.sitePackages}
  '';
}
