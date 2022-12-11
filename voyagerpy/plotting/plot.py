#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 25 14:08:42 2022

@author: sinant
"""


from math import ceil
from typing import (
    Any,
    Dict,
    Collection,
    Optional,
    Sequence,
    Tuple,
    Union,
)

import geopandas as gpd
import numpy as np

from anndata import AnnData
from copy import deepcopy
from matplotlib import cm
from matplotlib import colors
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from pandas import options

options.mode.chained_assignment = None  # default='warn'
from voyagerpy import spatial as spt

plt.style.use("ggplot")


def plot_spatial_features(
    adata: AnnData,
    features: Union[str, Sequence[str]],
    ncol: Optional[int] = None,
    barcode_geom: Optional[str] = None,
    annot_geom: Optional[str] = None,
    tissue: bool = True,
    colorbar: bool = False,
    cmap: Optional[str] = "Blues",
    categ_type: Union[str, Collection[str]] = {},
    geom_style: Optional[Dict] = {},
    annot_style: Optional[Dict] = {},
    alpha: float = 0.2,
    divergent: bool = False,
    color: Optional[str] = None,
    _ax: Optional[Axes] = None,
    legend: bool = True,
    subplot_kwds: Optional[Dict] = {},
    legend_kwds: Optional[Dict] = {},
    **kwds,
) -> Union[np.ndarray, Any]:

    if isinstance(features, list):
        feat_ls = features
    elif isinstance(features, str):
        feat_ls = [features]
    else:
        raise TypeError("features must be a string or a list of strings")

    # check input
    if ("geometry" not in adata.obs) or "geom" not in adata.uns["spatial"]:
        adata = spt.get_geom(adata)
    for i in feat_ls:
        if i not in adata.obs and i not in adata.var.index:
            raise ValueError(f"Cannot find {i!r} in adata.obs or gene names")
    # copy observation dataframe so we can edit it without changing the inputs
    obs = adata.obs

    # check if barcode geometry exists
    if barcode_geom is not None:
        if barcode_geom not in obs:
            raise ValueError(f"Cannot find {barcode_geom!r} data in adata.obs")

        # if barcode_geom is not spot polygons, change the default
        # geometry of the observation matrix, so we can plot it
        if barcode_geom != "spot_poly":
            obs.set_geometry(barcode_geom)

    # check if features are in rowdata

    # Check if too many subplots
    if len(feat_ls) > 6:
        raise ValueError("Too many features to plot, reduce the number of features")
    if ncol is not None:
        if ncol > 3:
            raise ValueError("Too many columns for subplots")

    # only work with spots in tissue
    if tissue:
        obs = obs[obs["in_tissue"] == 1]
    # use a divergent colormap
    if divergent:
        cmap = "Spectral"

    # create the subplots with right cols and rows
    if _ax is None:
        plt_nr = len(feat_ls)
        nrows = 1
        # ncols = ncol if ncol is not None else 1

        # defaults
        if ncol is None:
            if plt_nr < 4:
                ncols = plt_nr
            if plt_nr >= 4:
                nrows = 2
                ncols = 3

        else:
            nrows = ceil(plt_nr / ncols)

        # if(subplot_kwds is None):
        #     fig, axs = plt.subplots(nrows=nrows, ncols=ncols,figsize=(10,10))

        if "figsize" in subplot_kwds:
            fig, axs = plt.subplots(nrows=nrows, ncols=ncols, **subplot_kwds)
        else:

            # rat = row /col
            if nrows >= 2 and ncols == 3:
                _figsize = (10, 6)

            else:
                _figsize = (10, 10)
            fig, axs = plt.subplots(nrows=nrows, ncols=ncols, figsize=_figsize, **subplot_kwds)
            if plt_nr == 5:
                axs[-1, -1].axis("off")
        fig.tight_layout()  # Or equivalently,  "plt.tight_layout()"

        # plt.subplots_adjust(wspace = 1/ncols +  0.2)
    else:
        ncols = 1
        nrows = 1
        axs = _ax
    # iterate over features to plot
    x = 0
    y = 0

    for i in range(len(feat_ls)):
        legend_kwds_ = deepcopy(legend_kwds)
        _legend = legend
        if tissue:

            # if gene value
            if feat_ls[i] in adata.var.index:
                # col = adata.var[features]
                col = adata[adata.obs["in_tissue"] == 1, feat_ls[i]].X.todense().reshape((adata[adata.obs["in_tissue"] == 1, :].shape[0])).T

                col = np.array(col.ravel()).T
                obs[feat_ls[i]] = col
            if feat_ls[i] in obs.columns:
                # feat = features
                pass
        else:

            if feat_ls[i] in adata.var.index:
                # col = adata.var[features]
                col = adata[:, feat_ls[i]].X.todense().reshape((adata.shape[0])).T
                obs[feat_ls[i]] = col
            if feat_ls[i] in obs.columns:
                pass

        if ncols > 1 and nrows > 1:
            ax = axs[x, y]
        if ncols == 1 and nrows > 1:
            ax = axs[x]
        if nrows == 1 and ncols > 1:
            ax = axs[y]
        if ncols == 1 and nrows == 1:
            ax = axs

        if feat_ls[i] in adata.var.index or adata.obs[feat_ls[i]].dtype != "category":
            legend_kwds_.setdefault("label", feat_ls[i])
            legend_kwds_.setdefault("orientation", "vertical")
            legend_kwds_.setdefault("shrink", 0.4)
        else:
            #  colorbar for discrete categories if pandas column is categorical
            _legend = False
            catnr = adata.obs[feat_ls[i]].unique().shape[0]
            bounds = list(range(catnr + 1))
            norm = colors.BoundaryNorm(bounds, cm.get_cmap(cmap).N)
            ticks = list(range(catnr))
            ticks = [x + 0.5 for x in ticks]
            cbar = fig.colorbar(
                cm.ScalarMappable(cmap=cm.get_cmap(cmap), norm=norm),
                ax=ax,
                # extend="both",
                extendfrac="auto",
                ticks=ticks,
                spacing="uniform",
                orientation="vertical",
                # label=catname,
                shrink=0.5,
            )
            dd = list(adata.obs[feat_ls[i]].cat.categories)
            cc = cbar.ax.set_yticklabels(dd)
            cbar.ax.set_title(feat_ls[i])
        if color is not None:
            cmap = None

        obs.plot(
            feat_ls[i],
            ax=ax,
            color=color,
            legend=_legend,
            cmap=cmap,
            legend_kwds=legend_kwds_,
            **geom_style,
            **kwds,
        )
        if annot_geom is not None:
            if annot_geom in adata.uns["spatial"]["geom"]:

                # check annot_style is dict with correct values
                plg = adata.uns["spatial"]["geom"][annot_geom]
                if len(annot_style) != 0:
                    gpd.GeoSeries(plg).plot(ax=ax, **annot_style, **kwds)
                else:
                    gpd.GeoSeries(plg).plot(color="blue", ax=ax, alpha=alpha, **kwds)
            else:
                raise ValueError(f"Cannot find {annot_geom!r} data in adata.uns['spatial']['geom']")

            pass

        y = y + 1
        if y >= ncols:
            y = 0
            x = x + 1
    # colorbar title
    if _ax is not None:
        fig = ax.get_figure()
    axs = fig.get_axes()
    for i in range(len(axs)):
        if axs[i].properties()["label"] == "<colorbar>" and axs[i].properties()["ylabel"] != "":
            axs[i].set_title(axs[i].properties()["ylabel"], ha="left")
            axs[i].set_ylabel("")

    return axs  # ,fig
