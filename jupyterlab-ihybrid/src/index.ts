import {
  JupyterFrontEnd, JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { ICodeMirror } from '@jupyterlab/codemirror';

import { defineIHybridMode } from './codemirror-ihybrid';

/**
 * Initialization data for the extension1 extension.
 */
const extension: JupyterFrontEndPlugin<void> = {
  id: 'ihybrid',
  autoStart: true,
  requires: [ICodeMirror],
  activate: (app: JupyterFrontEnd, codeMirror: ICodeMirror) =>
  {
    defineIHybridMode(codeMirror).catch(console.warn);
  }
};

export default extension;
