{
  description = "agent-skills: the shared agent skills as Nix packages and a Home Manager module";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";

  outputs =
    { self, nixpkgs }:
    let
      lib = nixpkgs.lib;
      systems = [
        "x86_64-linux"
        "aarch64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
      ];
      forAllSystems = f: lib.genAttrs systems (system: f nixpkgs.legacyPackages.${system});

      # Every directory under skills/ is a skill; adding one needs no change here.
      skillNames = lib.attrNames (
        lib.filterAttrs (_: type: type == "directory") (builtins.readDir ./skills)
      );

      # Each skill is its own store path, so a change to one skill rebuilds only that
      # skill, and the source excludes Python's caches.
      skillSource =
        name:
        builtins.path {
          name = "agent-skill-${name}-source";
          path = ./skills + "/${name}";
          filter = path: _: !(lib.hasInfix "__pycache__" path || lib.hasSuffix ".pyc" path);
        };

      # A skill package installs the skill's directory, unchanged, as
      # share/agent-skills/<name>.
      mkSkill =
        pkgs: name:
        pkgs.runCommandLocal "agent-skill-${name}" { } ''
          mkdir -p $out/share/agent-skills
          cp -r ${skillSource name} $out/share/agent-skills/${name}
        '';
    in
    {
      # One package per skill, and `default` with all of them:
      #   nix build github:FactusConsulting/agent-skills#session-notes
      packages = forAllSystems (
        pkgs:
        let
          skills = lib.genAttrs skillNames (mkSkill pkgs);
        in
        skills
        // {
          default = pkgs.symlinkJoin {
            name = "agent-skills";
            paths = lib.attrValues skills;
          };
        }
      );

      # Links each skill into the user-level skill directories the harnesses read.
      # One link per skill, never the whole directory: vendor-managed skills (the Azure
      # pack, find-docs, ...) live beside them and keep their own updaters.
      homeManagerModules.default =
        {
          config,
          lib,
          pkgs,
          ...
        }:
        let
          cfg = config.programs.agent-skills;
          skillPackages = self.packages.${pkgs.stdenv.hostPlatform.system};
        in
        {
          options.programs.agent-skills = {
            enable = lib.mkEnableOption "the shared agent skills from FactusConsulting/agent-skills";
            skills = lib.mkOption {
              type = lib.types.listOf (lib.types.enum skillNames);
              default = skillNames;
              description = "The skills to install; all of them by default.";
            };
            directories = lib.mkOption {
              type = lib.types.listOf lib.types.str;
              # ~/.agents/skills is read by Pi, Codex, Copilot and Cursor;
              # ~/.claude/skills by Claude Code. A skill in both is loaded once per
              # harness, so no harness-specific directory (~/.pi/agent/skills,
              # ~/.codex/skills) is needed or wanted: it would load it twice.
              default = [
                ".agents/skills"
                ".claude/skills"
              ];
              description = "Skill directories, relative to the home directory.";
            };
          };

          config = lib.mkIf cfg.enable {
            home.file = lib.listToAttrs (
              lib.concatMap (
                dir:
                map (
                  name:
                  lib.nameValuePair "${dir}/${name}" {
                    source = "${skillPackages.${name}}/share/agent-skills/${name}";
                  }
                ) cfg.skills
              ) cfg.directories
            );
          };
        };

      checks = forAllSystems (
        pkgs:
        {
          # Every skill has SKILL.md with frontmatter whose name is its directory and
          # with a description, which is what harnesses match on, and announces itself
          # with an emoji of its own (README.md, Conventions).
          frontmatter =
            pkgs.runCommandLocal "agent-skills-frontmatter"
              {
                nativeBuildInputs = [ (pkgs.python3.withPackages (ps: [ ps.pyyaml ])) ];
              }
              ''
                python3 - ${self.packages.${pkgs.stdenv.hostPlatform.system}.default}/share/agent-skills <<'EOF'
                import pathlib, re, sys, yaml
                bad = []
                emojis = {}
                for d in sorted(pathlib.Path(sys.argv[1]).iterdir()):
                    f = d / "SKILL.md"
                    if not f.is_file():
                        bad.append(f"{d.name}: no SKILL.md"); continue
                    parts = f.read_text().split("---", 2)
                    meta = yaml.safe_load(parts[1]) if len(parts) == 3 and not parts[0].strip() else None
                    if not isinstance(meta, dict):
                        bad.append(f"{d.name}: SKILL.md has no frontmatter"); continue
                    if meta.get("name") != d.name:
                        bad.append(f"{d.name}: frontmatter name is {meta.get('name')!r}")
                    if not str(meta.get("description") or "").strip():
                        bad.append(f"{d.name}: no description")
                    m = re.search(r"^> \*\*Skill loaded:\*\* when you load this skill, announce it to the user as `(\S+) " + re.escape(d.name) + "`\\.$", parts[2], re.M)
                    if not m:
                        bad.append(f"{d.name}: no 'Skill loaded' announcement")
                    elif m.group(1) in emojis:
                        bad.append(f"{d.name}: emoji {m.group(1)} is also {emojis[m.group(1)]}'s")
                    else:
                        emojis[m.group(1)] = d.name
                print("\n".join(bad) or "all skills have valid frontmatter and an announcement")
                sys.exit(1 if bad else 0)
                EOF
                touch $out
              '';
        }
        # session-notes ships a validator with its own tests.
        // lib.optionalAttrs (builtins.elem "session-notes" skillNames) {
          session-notes =
            pkgs.runCommandLocal "agent-skill-session-notes-tests"
              {
                nativeBuildInputs = [
                  (pkgs.python3.withPackages (ps: [
                    ps.pytest
                    ps.pyyaml
                  ]))
                ];
              }
              ''
                cp -r ${skillSource "session-notes"} session-notes
                chmod -R u+w session-notes
                cd session-notes
                python3 -m pytest -q -p no:cacheprovider
                touch $out
              '';
        }
      );

      formatter = forAllSystems (pkgs: pkgs.nixfmt);
    };
}
