{ pkgs ? import <nixpkgs> {} }: with pkgs;
pkgs.mkShell {
  buildInputs = [
    rnix-lsp
  ];

  propagatedBuildInputs = with python3Packages; [
    poetry-core
    python39
  ];

  shellHook = ''
    export SOURCE_DATE_EPOCH=315532800
  '';
}
