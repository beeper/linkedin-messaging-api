{ pkgs ? import <nixpkgs> {} }: with pkgs;
pkgs.mkShell {
  buildInputs = [
    rnix-lsp
  ];

  propagatedBuildInputs = with python3Packages; [
    poetry
    python38
  ];

  shellHook = ''
    export SOURCE_DATE_EPOCH=315532800
  '';
}
