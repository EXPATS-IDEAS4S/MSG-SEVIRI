"""
Color constants and matplotlib style definitions
"""

import matplotlib as mpl
import cmcrameri.cm as cmc
import cartopy.crs as ccrs


CMAP = cmc.batlow
CMAP_an = cmc.vik
CMAP_discr = cmc.batlowW


mpl.rcParams["legend.frameon"] = False
mpl.rcParams["font.family"] = "sans-serif"
mpl.rcParams["font.sans-serif"] = [
    "Tahoma",
    "DejaVu Sans",
    "Lucida Grande",
    "Verdana",
]

mpl.rcParams["axes.spines.top"] = False
mpl.rcParams["axes.spines.right"] = False
mpl.rcParams["axes.grid"] = True

mpl.rcParams["savefig.dpi"] = 300
mpl.rcParams["savefig.bbox"] = "tight"
mpl.rcParams["savefig.transparent"] = True

def plot_cities_expats(ax, color, symbol_size):
    
    """add cities on a plot"""
    
    # set cities coordinates
    trento = [46.0667, 11.1167] #lat, lon
    bolzano = [46.4981, 11.3548]
    Munich = [48.137154, 11.576124]
    Innsbruck = [47.259659, 11.400375]
    Salzburg = [47.811195, 13.033229]
    Stuttgard = [48.783333, 9.183333]
    Zurich = [47.373878, 8.5450984]
    
    # Plot the points
    ax.scatter(trento[1], trento[0], marker='x', color=color, s=symbol_size, transform=ccrs.PlateCarree())
    ax.scatter(bolzano[1], bolzano[0], marker='x', color=color, s=symbol_size, transform=ccrs.PlateCarree())
    ax.scatter(Innsbruck[1], Innsbruck[0], marker='x', color=color, s=symbol_size, transform=ccrs.PlateCarree())
    ax.scatter(Munich[1], Munich[0], marker='x', color=color, s=symbol_size, transform=ccrs.PlateCarree())
    ax.scatter(Salzburg[1], Salzburg[0], marker='x', color=color, s=symbol_size, transform=ccrs.PlateCarree())
    ax.scatter(Stuttgard[1], Stuttgard[0], marker='x', color=color, s=symbol_size, transform=ccrs.PlateCarree())
    ax.scatter(Zurich[1], Zurich[0], marker='x', color=color, s=symbol_size, transform=ccrs.PlateCarree())

    
    # Plot the names next to the points, adjusted for lower right positioning
    ax.text(trento[1] + 0.02, trento[0] - 0.02, 'Trento', color=color, transform=ccrs.PlateCarree(), ha='left', va='top')
    ax.text(bolzano[1] + 0.02, bolzano[0] - 0.02, 'Bolzano', color=color, transform=ccrs.PlateCarree(), ha='left', va='top')
    ax.text(Innsbruck[1] + 0.02, Innsbruck[0] - 0.02, 'Innsbruck', color=color, transform=ccrs.PlateCarree(), ha='left', va='top')
    ax.text(Munich[1] + 0.02, Munich[0] - 0.02, 'Munich', color=color, transform=ccrs.PlateCarree(), ha='left', va='top')
    ax.text(Salzburg[1] + 0.02, Salzburg[0] - 0.02, 'Salzburg', color=color, transform=ccrs.PlateCarree(), ha='left', va='top')
    ax.text(Stuttgard[1] + 0.02, Stuttgard[0] - 0.02, 'Stuttgard', color=color, transform=ccrs.PlateCarree(), ha='left', va='top')
    ax.text(Zurich[1] + 0.02, Zurich[0] - 0.02, 'Zurich', color=color, transform=ccrs.PlateCarree(), ha='left', va='top')

    return

    
    
def plot_local_dfg(ax, color, symbol_size):
    
    
    #add instrument positions 
    Penegal = [46.43921, 11.2155]
    Tarmeno = [46.34054, 11.2545]
    Vilpiano = [46.55285, 11.20195]
    Sarntal = [46.56611, 11.51642]
    Cles_Malgolo = [46.38098, 11.08136]
    trento = [46.0667, 11.1167] #lat, lon
    bolzano = [46.4981, 11.3548]  
    
     
    ax.scatter(trento[1], trento[0], marker='x', color=color, s=symbol_size, transform=ccrs.PlateCarree())
    ax.scatter(bolzano[1], bolzano[0], marker='x', color=color, s=symbol_size, transform=ccrs.PlateCarree())
    ax.scatter(Penegal[1], Penegal[0], marker='x', color=color, s=symbol_size, transform=ccrs.PlateCarree())
    ax.scatter(Cles_Malgolo[1], Cles_Malgolo[0], marker='x', color=color, s=symbol_size, transform=ccrs.PlateCarree())                        
    ax.scatter(Tarmeno[1], Tarmeno[0], marker='x', color=color, s=symbol_size, transform=ccrs.PlateCarree())            
    ax.scatter(Vilpiano[1], Vilpiano[0], marker='x', color=color, s=symbol_size, transform=ccrs.PlateCarree())            
    ax.scatter(Sarntal[1], Sarntal[0], marker='x', color=color, s=symbol_size, transform=ccrs.PlateCarree())            

    ax.text(trento[1] + 0.02, trento[0] - 0.02, 'Trento', color=color, transform=ccrs.PlateCarree(), ha='left', va='top')
    ax.text(bolzano[1] + 0.02, bolzano[0] - 0.02, 'Bolzano', color=color, transform=ccrs.PlateCarree(), ha='left', va='top')
    ax.text(Penegal[1] + 0.02, Penegal[0] - 0.02, 'Penegal', color=color, transform=ccrs.PlateCarree(), ha='left', va='top')
    ax.text(Cles_Malgolo[1] + 0.02, Cles_Malgolo[0] - 0.02, 'Cles_Malgolo', color=color, transform=ccrs.PlateCarree(), ha='left', va='top')
    ax.text(Tarmeno[1] + 0.02, Tarmeno[0] - 0.02, 'Tarmeno', color=color, transform=ccrs.PlateCarree(), ha='left', va='top')
    ax.text(Vilpiano[1] + 0.02, Vilpiano[0] - 0.02, 'Vilpiano', color=color, transform=ccrs.PlateCarree(), ha='left', va='top')
    ax.text(Sarntal[1] + 0.02, Sarntal[0] - 0.02, 'Sarntal', color=color, transform=ccrs.PlateCarree(), ha='left', va='top')
    
    return

