# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


added_files = [("resources/images/exit@256px.png", "resources/images"),
			   ("resources/images/button-help-3@256px.png", "resources/images"),
			   ("resources/images/button-ok-3@256px.png", "resources/images"),
			   ("resources/images/save-filled-table@256px.png", "resources/images"),
			   ("resources/images/save-filled-text-box@256px.png", "resources/images"),
			   ("resources/images/save-filled-picture-filled@256px.png", "resources/images"),
			   ("resources/images/format-decimal@256px.png", "resources/images"),
			   ("resources/images/tool-calculator-filled@256px.png", "resources/images"),
			   ("resources/images/button-cancel-3@256px.png", "resources/images"),
			   ("resources/images/folder-action-open-filled@256px.png", "resources/images"),
			   ("resources/images/table-eraser@256px.png", "resources/images"),
			   ("resources/images/tool-ruler-filled@256px.png", "resources/images"),
			   ("resources/images/sum-work-filled@256px.png", "resources/images"),
			   ("resources/images/document-text@256px.png", "resources/images"),
			   ("resources/images/table@256px.png", "resources/images"),
			   ("resources/images/charts-line-color@256px.png", "resources/images"),
			   ("resources/images/draw-radial-plot@256px.png", "resources/images"),
		       ("resources/images/chart-forest-plot@256px.png", "resources/images"),
		       ("resources/images/letter-z-2@256px.png", "resources/images"),
			   ("resources/images/phylogeny@256px.png", "resources/images"),
			   ("resources/images/draw-points@256px.png", "resources/images"),
			   ("resources/images/charts-filled@256px.png", "resources/images"),
			   ("resources/images/gear-filled@256px.png", "resources/images"),
			   ("resources/images/filter-filled-eraser@256px.png", "resources/images"),
			   ("resources/images/table-column-color-wheel@256px.png", "resources/images"),
			   ("resources/images/table-row-color-wheel@256px.png", "resources/images"),
			   ("resources/images/text-fonts@256px.png", "resources/images"),
			   ("resources/images/picture-edit-filled@256px.png", "resources/images"),
			   ("resources/images/data-export@256px.png", "resources/images"),
			   ("resources/images/letter-alpha@256px.png", "resources/images"),
			   ("resources/images/translation@256px.png", "resources/images"),
			   ("resources/images/toolbar-position-left-add-filled@256px.png", "resources/images"),
			   ("resources/images/toolbar-position-left-cancel-filled@256px.png", "resources/images"),
			   ("resources/images/metawin3toolbar_icon.png", "resources/images"),
			   ("resources/images/metawin3splash_square.png", "resources/images"),
			   ("resources/images/cloud-filled-download-filled@256px.png", "resources/images"),
			   ("resources/images/flag-united-states@256px.png", "resources/images"),
			   ("resources/images/flag-spain@256px.png", "resources/images"),

			   ("resources/images/metawin3icon.png", "resources/images"),
			   ("resources/images/draw_forest.png", "resources/images"),
			   ("resources/images/draw_histogram.png", "resources/images"),
			   ("resources/images/draw_normal_quantile.png", "resources/images"),
			   ("resources/images/draw_radial.png", "resources/images"),
			   ("resources/images/draw_scatter.png", "resources/images"),
			   ("resources/images/example_scatter.png", "resources/images"),
			   ("resources/images/example_histogram.png", "resources/images"),
			   ("resources/images/example_forest.png", "resources/images"),
			   ("resources/images/example_normal_quantile.png", "resources/images"),
			   ("resources/images/example_radial.png", "resources/images"),
			   ("resources/images/graph_tab.png", "resources/images"),
			   ("resources/images/graph_edit.png", "resources/images"),
			   ("resources/images/import_data_dialog.png", "resources/images"),
			   ("resources/images/main_window.png", "resources/images"),
			   ("resources/images/output_tab.png", "resources/images"),
			   ("resources/images/phylogeny_tab.png", "resources/images"),
			   ("resources/images/phylogeny_tab_loaded.png", "resources/images"),
			   ("resources/images/save_data_dialog.png", "resources/images"),
			   ("resources/images/effects_r.png", "resources/images"),
			   ("resources/images/effects_p.png", "resources/images"),
			   ("resources/images/effects_means.png", "resources/images"),
			   ("resources/images/effects_2x2.png", "resources/images"),
			   ("resources/images/mw1_cover.jpg", "resources/images"),
			   ("resources/images/mw2_cover.jpg", "resources/images"),
			   ("resources/images/analysis_basic1.png", "resources/images"),
			   ("resources/images/analysis_basic2.png", "resources/images"),
			   ("resources/images/analysis_basic_fig.png", "resources/images"),
			   ("resources/images/analysis_dialog.png", "resources/images"),
			   ("resources/images/analysis_jackknife_dialog1.png", "resources/images"),
			   ("resources/images/analysis_jackknife_dialog2.png", "resources/images"),
			   ("resources/images/analysis_jackknife_fig.png", "resources/images"),
			   ("resources/images/analysis_trim_fill_fig.png", "resources/images"),
			   ("resources/images/analysis_trim_fill_dialog.png", "resources/images"),
			   ("resources/images/analysis_rank_cor_dialog.png", "resources/images"),
			   ("resources/images/analysis_cumulative_fig.png", "resources/images"),
			   ("resources/images/analysis_cumulative1.png", "resources/images"),
			   ("resources/images/analysis_cumulative2.png", "resources/images"),
			   ("resources/images/analysis_grouped_fig.png", "resources/images"),
			   ("resources/images/analysis_grouped1.png", "resources/images"),
			   ("resources/images/analysis_grouped2.png", "resources/images"),
			   ("resources/images/analysis_nested_fig.png", "resources/images"),
			   ("resources/images/analysis_nested1.png", "resources/images"),
			   ("resources/images/analysis_nested2.png", "resources/images"),
			   ("resources/images/analysis_glm1.png", "resources/images"),
			   ("resources/images/analysis_glm2.png", "resources/images"),
			   ("resources/images/analysis_regression_fig.png", "resources/images"),
			   ("resources/images/analysis_regression1.png", "resources/images"),
			   ("resources/images/analysis_regression2.png", "resources/images"),
			   ("resources/images/metacalc.png", "resources/images"),

			   ("resources/metawin.css", "resources"),
			   ("resources/metacalc_help.html", "resources"),
               ("resources/metawin_help.html", "resources")]

a = Analysis(
    ['src/MetaWin.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

splash = Splash("resources/images/metawin3splash_square.png",
                binaries=a.binaries,
                datas=a.datas,
                text_pos=None,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
	splash,
	splash.binaries,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MetaWin',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
	icon="resources/images/metawin3icon.ico",
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
