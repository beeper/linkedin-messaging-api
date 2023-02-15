{ pkgs ? import <nixpkgs> {} }: with pkgs;
pkgs.mkShell {
  buildInputs = [
    rnix-lsp
  ];

  propagatedBuildInputs = with python3Packages; [
    python39
  ];

  shellHook = ''
    export SOURCE_DATE_EPOCH=315532800
  '';
}
