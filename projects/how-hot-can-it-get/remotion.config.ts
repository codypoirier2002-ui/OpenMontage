// Remotion CLI config for rendering THROUGH the symlink
//   remotion-composer/projects/how-hot-can-it-get -> ../../projects/how-hot-can-it-get
// webpack resolves the symlink to its real path, from which no node_modules is reachable, so
// packages other than remotion/react (e.g. @remotion/google-fonts) would fail to resolve.
// This adds remotion-composer/node_modules as a module directory. Pass it with --config (still.sh does).
// video_compose's atelier render does not need it: it stages real copies inside remotion-composer/.
import path from "node:path";
import { Config } from "@remotion/cli/config";

const composerNodeModules = path.resolve(process.cwd(), "node_modules");

Config.overrideWebpackConfig((config) => ({
  ...config,
  resolve: {
    ...config.resolve,
    modules: [...(config.resolve?.modules ?? ["node_modules"]), composerNodeModules],
  },
}));
