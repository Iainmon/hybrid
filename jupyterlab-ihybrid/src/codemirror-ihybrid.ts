import { ICodeMirror, Mode } from '@jupyterlab/codemirror';

export async function defineIHybridMode({ CodeMirror }: ICodeMirror) {
  await Mode.ensure("hybrid");
  await Mode.ensure("r");
  CodeMirror.defineMode("ihybrid", (config) => {
    let hmode = CodeMirror.getMode(config, "hybrid");
    return CodeMirror.multiplexingMode(
      hmode,
      {
        // @ts-ignore
        open: /:(?=!)/, // Matches : followed by !, but doesn't consume !
        // @ts-ignore
        close: /^(?!!)/, // Matches start of line not followed by !, doesn't consume character
        mode: CodeMirror.getMode(config, "text/plain"),
        delimStyle: "delimit"
      },
      {
        // @ts-ignore
        open: /\[r\||\[rprint\||\[rgraph\|/,
        // @ts-ignore
        close: /\|\]/,
        mode: CodeMirror.getMode(config, "text/x-rsrc"),
        delimStyle: "delimit"
      }
    );
  });

  CodeMirror.defineMIME("text/x-ihybrid", "ihybrid");

  CodeMirror.modeInfo.push({
    ext: ['hs'],
    mime: "text/x-ihybrid",
    mode: 'ihybrid',
    name: 'ihybrid'
  });
}
