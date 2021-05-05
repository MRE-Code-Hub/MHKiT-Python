import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from mhkit.wave.resource import significant_wave_height as _sig_wave_height
from mhkit.wave.resource import peak_period as _peak_period
from mhkit.river.graphics import _xy_plot
from matplotlib import gridspec
from matplotlib import pylab
import datetime


def plot_spectrum(S, ax=None):
    """
    Plots wave amplitude spectrum versus omega
    Parameters
    ------------
    S: pandas DataFrame
        Spectral density [m^2/Hz] indexed frequency [Hz]
    ax : matplotlib axes object
        Axes for plotting.  If None, then a new figure is created.
    Returns
    ---------
    ax : matplotlib pyplot axes
    """
    assert isinstance(S, pd.DataFrame), 'S must be of type pd.DataFrame'

    f = S.index

    ax = _xy_plot(f*2*np.pi, S/(2*np.pi), fmt='-', xlabel='omega [rad/s]',
             ylabel='Spectral density [m$^2$s/rad]', ax=ax)


    return ax

def plot_elevation_timeseries(eta, ax=None):
    """
    Plot wave surface elevation time-series
    Parameters
    ------------
    eta: pandas DataFrame
        Wave surface elevation [m] indexed by time [datetime or s]
    ax : matplotlib axes object
        Axes for plotting.  If None, then a new figure is created.
    Returns
    ---------
    ax : matplotlib pyplot axes
    """

    assert isinstance(eta, pd.DataFrame), 'eta must be of type pd.DataFrame'

    ax = _xy_plot(eta.index, eta, fmt='-', xlabel='Time',
                  ylabel='$\eta$ [m]', ax=ax)

    return ax

def plot_matrix(M, xlabel='Te', ylabel='Hm0', zlabel=None, show_values=True,
                ax=None):
    """
    Plots values in the matrix as a scatter diagram
    
    Parameters
    ------------
    M: pandas DataFrame
        Matrix with numeric labels for x and y axis, and numeric entries.
        An example would be the average capture length matrix generated by
        mhkit.device.wave, or something similar.
    xlabel: string (optional)
        Title of the x-axis
    ylabel: string (optional)
        Title of the y-axis
    zlabel: string (optional)
        Colorbar label
    show_values : bool (optional)
        Show values on the scatter diagram
    ax : matplotlib axes object
        Axes for plotting.  If None, then a new figure is created.
    Returns
    ---------
    ax : matplotlib pyplot axes
    """
    
    assert isinstance(M, pd.DataFrame), 'M must be of type pd.DataFrame'

    if ax is None:
        plt.figure()
        ax = plt.gca()

    im = ax.imshow(M, origin='lower', aspect='auto')

    # Add colorbar
    cbar = plt.colorbar(im)
    if zlabel:
        cbar.set_label(zlabel, rotation=270, labelpad=15)

    # Set x and y label
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    # Show values in the plot
    if show_values:
        for i, col in enumerate(M.columns):
            for j, index in enumerate(M.index):
                if not np.isnan(M.loc[index,col]):
                    ax.text(i, j, format(M.loc[index,col], '.2f'), ha="center", va="center")

    # Reset x and y ticks
    ax.set_xticks(np.arange(len(M.columns)))
    ax.set_yticks(np.arange(len(M.index)))
    ax.set_xticklabels(M.columns)
    ax.set_yticklabels(M.index)

    return ax


def plot_chakrabarti(H, lambda_w, D, ax=None):
    """
    Plots, in the style of Chakrabart (2005), relative importance of viscous,
    inertia, and diffraction phemonena
    Chakrabarti, Subrata. Handbook of Offshore Engineering (2-volume set).
    Elsevier, 2005.
    Parameters
    ------------
    H: float or numpy array or pandas Series
        Wave height [m]
    lambda_w: float or numpy array or pandas Series
        Wave length [m]
    D: float or numpy array or pandas Series
        Characteristic length [m]
    ax : matplotlib axes object (optional)
        Axes for plotting.  If None, then a new figure is created.
    Returns
    ---------
    ax : matplotlib pyplot axes
    Examples
    --------
    **Using floats**
    >>> plt.figure()
    >>> D = 5
    >>> H = 8
    >>> lambda_w = 200
    >>> wave.graphics.plot_chakrabarti(H, lambda_w, D)
    **Using numpy array**
    >>> plt.figure()
    >>> D = np.linspace(5,15,5)
    >>> H = 8*np.ones_like(D)
    >>> lambda_w = 200*np.ones_like(D)
    >>> wave.graphics.plot_chakrabarti(H, lambda_w, D)
    **Using pandas DataFrame**
    >>> plt.figure()
    >>> D = np.linspace(5,15,5)
    >>> H = 8*np.ones_like(D)
    >>> lambda_w = 200*np.ones_like(D)
    >>> df = pd.DataFrame([H.flatten(),lambda_w.flatten(),D.flatten()], \
                              index=['H','lambda_w','D']).transpose()
    >>> wave.graphics.plot_chakrabarti(df.H, df.lambda_w, df.D)
    """
    assert isinstance(H, (np.ndarray, float, int, np.int64,pd.Series)), \
           'H must be a real numeric type'
    assert isinstance(lambda_w, (np.ndarray, float, int, np.int64,pd.Series)), \
           'lambda_w must be a real numeric type'
    assert isinstance(D, (np.ndarray, float, int, np.int64,pd.Series)), \
           'D must be a real numeric type'

    if any([(isinstance(H, np.ndarray) or isinstance(H, pd.Series)),        \
            (isinstance(lambda_w, np.ndarray) or isinstance(H, pd.Series)), \
            (isinstance(D, np.ndarray) or isinstance(H, pd.Series))\
           ]):
        errMsg = 'D, H, and lambda_w must be same shape'
        n_H = H.squeeze().shape
        n_lambda_w = lambda_w.squeeze().shape
        n_D = D.squeeze().shape
        assert n_H == n_lambda_w and n_H == n_D, errMsg

        if isinstance(H, np.ndarray):
            mvals = pd.DataFrame(H.reshape(len(H),1), columns=['H'])
            mvals['lambda_w'] = lambda_w
            mvals['D'] = D
        elif isinstance(H, pd.Series):
            mvals = pd.DataFrame(H)
            mvals['lambda_w'] = lambda_w
            mvals['D'] = D

    else:
        H = np.array([H])
        lambda_w = np.array([lambda_w])
        D = np.array([D])
        mvals = pd.DataFrame(H.reshape(len(H),1), columns=['H'])
        mvals['lambda_w'] = lambda_w
        mvals['D'] = D

    if ax is None:
        plt.figure()
        ax = plt.gca()

    ax.set_xscale('log')
    ax.set_yscale('log')

    for index, row in mvals.iterrows():
        H = row.H
        D = row.D
        lambda_w = row.lambda_w
        
        KC = H / D
        Diffraction = np.pi*D / lambda_w
        label = f'$H$ = {H:g}, $\lambda_w$ = {lambda_w:g}, $D$ = {D:g}'
        ax.plot(Diffraction, KC, 'o', label=label)
   
    if np.any(KC>=10 or KC<=.02) or np.any(Diffraction>=50) or \
        np.any(lambda_w >= 1000) :
        ax.autoscale(enable=True, axis='both', tight=True)  
    else:
        ax.set_xlim((0.01, 10))
        ax.set_ylim((0.01, 50))

    graphScale = list(ax.get_xlim())
    if graphScale[0] >= .01:
        graphScale[0] =.01

    # deep water breaking limit (H/lambda_w = 0.14)
    x = np.logspace(1,np.log10(graphScale[0]), 2)
    y_breaking = 0.14 * np.pi / x
    ax.plot(x, y_breaking, 'k-')
    graphScale = list(ax.get_xlim())
    
    ax.text(1, 7, 
            'wave\nbreaking\n$H/\lambda_w > 0.14$', 
            ha='center', va='center', fontstyle='italic', 
            fontsize='small',clip_on='True')

    # upper bound of low drag region
    ldv = 20
    y_small_drag = 20*np.ones_like(graphScale)
    graphScale[1] = 0.14 * np.pi / ldv
    ax.plot(graphScale, y_small_drag,'k--')
    ax.text(0.0125, 30, 
            'drag', 
            ha='center', va='top', fontstyle='italic',
            fontsize='small',clip_on='True')
            
    # upper bound of small drag region
    sdv = 1.5
    y_small_drag = sdv*np.ones_like(graphScale)
    graphScale[1] = 0.14 * np.pi / sdv
    ax.plot(graphScale, y_small_drag,'k--')
    ax.text(0.02, 7, 
            'inertia \n& drag', 
            ha='center', va='center', fontstyle='italic', 
            fontsize='small',clip_on='True')

    # upper bound of negligible drag region
    ndv = 0.25
    graphScale[1] = 0.14 * np.pi / ndv
    y_small_drag = ndv*np.ones_like(graphScale)
    ax.plot(graphScale, y_small_drag,'k--')
    ax.text(8e-2, 0.7, 
            'large\ninertia', 
            ha='center', va='center', fontstyle='italic', 
            fontsize='small',clip_on='True')


    ax.text(8e-2, 6e-2, 
            'all\ninertia', 
            ha='center', va='center', fontstyle='italic', 
            fontsize='small', clip_on='True')

    # left bound of diffraction region
    drv = 0.5
    graphScale = list(ax.get_ylim())
    graphScale[1] = 0.14 * np.pi / drv
    x_diff_reg = drv*np.ones_like(graphScale)
    ax.plot(x_diff_reg, graphScale, 'k--')
    ax.text(2, 6e-2, 
            'diffraction', 
            ha='center', va='center', fontstyle='italic',
            fontsize='small',clip_on='True')


    if index > 0:
        ax.legend(fontsize='xx-small', ncol=2)

    ax.set_xlabel('Diffraction parameter, $\\frac{\\pi D}{\\lambda_w}$')
    ax.set_ylabel('KC parameter, $\\frac{H}{D}$')

    plt.tight_layout()

def plot_environmental_contour(x1, x2, x1_contour, x2_contour, **kwargs):
    '''
    Plots an overlay of the x1 and x2 variables to the calculate
    environmental contours.
    Parameters
    ----------
    x1: numpy array  
        x-axis data
    x2: numpy array 
        x-axis data
    x1_contour: numpy array 
        Calculated x1 contour values
    x2_contour: numpy array 
        Calculated x2 contour values 
    **kwargs : optional         
        x_label: string (optional)
            x-axis label. Default None. 
        y_label: string (optional)
            y-axis label. Default None.
        data_label: string (optional)
            Legend label for x1, x2 data (e.g. 'Buoy 46022'). 
            Default None.
        contour_label: string or list of strings (optional)
            Legend label for x1_contour, x2_contour countor data 
            (e.g. '100-year contour'). Default None.
        ax : matplotlib axes object (optional)
            Axes for plotting.  If None, then a new figure is created.
            Default None.
    Returns
    -------
    ax : matplotlib pyplot axes
    '''
    
    assert isinstance(x1, np.ndarray), 'x1 must be of type np.ndarray'
    assert isinstance(x2, np.ndarray), 'x2 must be of type np.ndarray'
    assert isinstance(x1_contour, np.ndarray), ('x1_contour must be of '
                                                'type np.ndarray')
    assert isinstance(x2_contour, np.ndarray), ('x2_contour must be of '
                                               'type np.ndarray')
    x_label = kwargs.get("x_label", None)
    y_label = kwargs.get("y_label", None)
    data_label=kwargs.get("data_label", None)
    contour_label=kwargs.get("contour_label", None)
    ax=kwargs.get("ax", None)
    assert isinstance(data_label, str), 'data_label must be of type str'
    assert isinstance(contour_label, (str,list)), ('contour_label be of '
                                                  'type str')
    assert x2_contour.ndim == x1_contour.ndim,  ('contour must be of' 
            f'equal dimesion got {x2_contour.ndim} and {x1_contour.ndim}')                                                  
    
        
    if x2_contour.ndim == 1:
        x2_contour  = x2_contour.reshape(-1,1) 
        x1_contour = x1_contour.reshape(-1,1) 
    
    N_contours = x2_contour.shape[1]
    
    if contour_label != None:
        if isinstance(contour_label, str):
            contour_label = [contour_label] 
        N_c_labels = len(contour_label)
        assert  N_c_labels == N_contours, ('If specified, the '
             'number of contour lables must be equal to number the '
            f'number of contour years. Got {N_c_labels} and {N_contours}')   
    else:
        contour_label = [None] * N_contours
    
    for i in range(N_contours):       
        ax = _xy_plot(x1_contour[:,i], x2_contour[:,i],'-', 
                      label=contour_label[i], ax=ax)
            
    ax = plt.plot(x1, x2, 'bo', alpha=0.1, 
                  label=data_label) 
    plt.legend(loc='lower right')
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.tight_layout()
    return ax


def plot_compendium(Hs, Tp, Dp, buoytitle=None, ax=None):
    """
    Create subplots showing: Significant Wave Height (Hs), Peak Period (Tp), 
    and Direction (Dp) using OPeNDAP service from CDIP THREDDS Server.
    
    See http://cdip.ucsd.edu/themes/cdip?pb=1&bl=cdip?pb=1&d2=p70&u3=s:100:st:1:v:compendium:dt:201204 for example Compendium plot.
    
    Developed based on: http://cdip.ucsd.edu/themes/media/docs/documents/html_pages/compendium.html

    Parameters
    ------------
    data: pandas DataFrame
        Spectral density [m^2/Hz] indexed frequency [Hz]
    buoytitle: string (optional)
        Buoy title from the CDIP THREDDS Server
    ax : matplotlib axes object (optional)
        Axes for plotting.  If None, then a new figure is created.
    Returns
    ---------
    ax : matplotlib pyplot axes

    """

    f, (pHs, pTp, pDp) = plt.subplots(3, 1, sharex=True, figsize=(15,10)) 
    
    pHs.plot(Hs.index,Hs,'b')
    pTp.plot(Tp.index,Tp,'b')
    pDp.scatter(Dp.index,Dp,color='blue',s=5) 
    
    pHs.tick_params(axis='x', which='major', labelsize=12, top='off')
    pHs.set_ylim(0,8)
    pHs.tick_params(axis='y', which='major', labelsize=12, right='off')
    pHs.set_ylabel('Hs [m]', fontsize=18)
    pHs.grid(b=True, which='major', color='b', linestyle='--')

    pHs2 = pHs.twinx()
    pHs2.set_ylim(0,25)
    pHs2.set_ylabel('Hs [ft]', fontsize=18)

    
    # Peak Period, Tp
    pTp.set_ylim(0,28)
    pTp.set_ylabel('Tp [s]', fontsize=18)
    pTp.grid(b=True, which='major', color='b', linestyle='--')
    
    
    # Direction, Dp 
    pDp.set_ylim(0,360)
    pDp.set_ylabel('Dp [deg]', fontsize=18)
    pDp.grid(b=True, which='major', color='b', linestyle='--')
    pDp.set_xlabel('Day', fontsize=18)
    
    # Set x-axis tick interval to every 5 days
    degrees = 70    
    days = matplotlib.dates.DayLocator(interval=5) 
    daysFmt = matplotlib.dates.DateFormatter('%Y-%m-%d')
    plt.gca().xaxis.set_major_locator(days)
    plt.gca().xaxis.set_major_formatter(daysFmt)
    plt.setp( pDp.xaxis.get_majorticklabels(), rotation=degrees )

    # Set Titles
    month_name_start = Hs.index.month_name()[0][:3]
    year_start = Hs.index.year[0]
    month_name_end = Hs.index.month_name()[-1][:3]
    year_end = Hs.index.year[-1]
    plt.suptitle(buoytitle, fontsize=30) 
    
    plt.title(f'{Hs.index[0].date()} to {Hs.index[-1].date()}', fontsize=20)

    ax = f

    return ax


def plot_boxplot(Hs, buoytitle=None):
    """
    Create plot of monthly-averaged boxes of Significant Wave Height (Hs) data across one year using OPeNDAP service from CDIP THREDDS Server.

    See http://cdip.ucsd.edu/themes/cdip?pb=1&bl=cdip?pb=1&d2=p70&u3=s:093:st:1:v:hs_box_plot:dt:2011 for example Hs Boxplot.

    Developed based on: http://cdip.ucsd.edu/themes/media/docs/documents/html_pages/annualHs_plot.html
    
    Parameters
    ------------
    data: pandas DataFrame
        Spectral density [m^2/Hz] indexed frequency [Hz]
    buoytitle: string (optional)
        Buoy title from the CDIP THREDDS Server
    ax : matplotlib axes object (optional)
        Axes for plotting.  If None, then a new figure is created.
    Returns
    ---------
    ax : matplotlib pyplot axes
    """
   
    months = Hs.index.month
    means = Hs.groupby(months).mean()
    monthlengths = Hs.groupby(months).count()
    
    fig = plt.figure(figsize=(10,12)) 
    gs = gridspec.GridSpec(2,1, height_ratios=[4,1]) 
    
    boxprops = dict(color='k')
    whiskerprops = dict(linestyle='--', color='k')
    flierprops = dict(marker='+', color='r',markeredgecolor='r',markerfacecolor='r')
    medianprops = dict(linewidth=2.5,color='firebrick')
    meanprops = dict(linewidth=2.5, marker='_',  markersize=25)
    
    bp = plt.subplot(gs[0,:])    
    
    Hs_months = Hs.to_frame().groupby(months)
    bp = Hs_months.boxplot(subplots=False, boxprops=boxprops,
        whiskerprops=whiskerprops, flierprops=flierprops,
        medianprops=medianprops, showmeans=True, meanprops=meanprops)
    
    # Add values of monthly means as text
    for i, mean in enumerate(means):
        bp.annotate(np.round(mean,2), (means.index[i],mean),fontsize=12,
                    horizontalalignment='center',verticalalignment='bottom',
                    color='g')

    #Create a second row of x-axis labels for top subplot
    newax = bp.twiny()
    newax.tick_params(which='major', direction='in', pad=-18)
    newax.set_xlim(bp.get_xlim())
    newax.xaxis.set_ticks_position('top')
    newax.xaxis.set_label_position('top')
    newax.set_xticks(np.arange(1,13,1)) 
    newax.set_xticklabels(monthlengths,fontsize=10)
                       

    # Sample 'legend' boxplot, to go underneath actual boxplot
    bp_sample2 = np.random.normal(2.5,0.5,500)        
    bp2 = plt.subplot(gs[1,:])
    meanprops = dict(linewidth=2.5, marker='|',  markersize=25)
    bp2_example = bp2.boxplot(bp_sample2,vert=False,flierprops=flierprops, 
                        medianprops=medianprops) 
    sample_mean=2.3
    bp2.scatter(sample_mean,1,marker="|",color='g',linewidths=1.0,s=200)
    
    for line in bp2_example['medians']:
        xm, ym = line.get_xydata()[0] 
    for line in bp2_example['boxes']:
        xb, yb = line.get_xydata()[0] 
    for line in bp2_example['whiskers']:
        xw, yw = line.get_xydata()[0] 
    
    bp2.annotate("Median",[xm-0.1,ym-0.3*ym],fontsize=10,color='firebrick')
    bp2.annotate("Mean",[sample_mean-0.1,0.65],fontsize=10,color='g')
    bp2.annotate("25%ile",[xb-0.05*xb,yb-0.15*yb],fontsize=10)
    bp2.annotate("75%ile",[xb+0.26*xb,yb-0.15*yb],fontsize=10)
    bp2.annotate("Outliers",[xw+0.3*xw,yw-0.3*yw],fontsize=10,color='r')
       

    if buoytitle:
        plt.suptitle(buoytitle, fontsize=30, y=0.97)
    bp.set_title("Significant Wave Height by Month", fontsize=20, y=1.01)
    bp2.set_title("Sample Boxplot", fontsize=10, y=1.02)
    
    # Set axes labels and ticks    
    months_text = [ m[:3] for m in Hs.index.month_name().unique()]
    bp.set_xticklabels(months_text,fontsize=12)
    bp.set_ylabel('Significant Wave Height, Hs (m)', fontsize=14)
    bp.tick_params(axis='y', which='major', labelsize=12, right='off')
    bp.tick_params(axis='x', which='major', labelsize=12, top='off')
    

    
    # Plot horizontal gridlines onto top subplot
    bp.grid(axis='x', which='major', color='b', linestyle='-', alpha=0.25)
    
    # Remove tickmarks from bottom subplot
    bp2.axes.get_xaxis().set_visible(False)
    bp2.axes.get_yaxis().set_visible(False)

    ax = fig

    return ax
