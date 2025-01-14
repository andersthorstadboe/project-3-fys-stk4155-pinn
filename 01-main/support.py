import autograd.numpy as anp
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

## --- Activation functions --- ##
def identity(z):
    return z

def sigmoid(z):
    return 1 / (1 + anp.exp(-z))

def tanh(z):
    return anp.tanh(z)

def ReLU(z):
    return anp.where(z > 0, z, 0)

def LeakyReLU(z,alpha=0.01):
    return anp.where(z > 0, z, alpha*z)

def ELU(z,alpha=1.):
    return anp.where(z > 0, z, alpha*(anp.exp(z)-1))

def GELU(z):
    a = 0.044715
    return 0.5*z*(1 + anp.tanh(anp.sqrt(2/anp.pi)*(z + a*z**3)))
def SiLU(z):
    return z*sigmoid(z)

## --- Gradient Descent methods --- ##
class GDTemplate:
    def __init__(self,learning_rate=0.01):
        self.eta = learning_rate

    def update_change(self,gradient,theta_m1):
        raise RuntimeError
    
    def reset(self):
        pass


class PlainGD(GDTemplate):
    def __init__(self, learning_rate=0.01,
                 lmbda=0.0,
                 lp=0):
        super().__init__(learning_rate)
        self.lmbda = lmbda
        self.lp = lp

    def update_change(self, gradient,theta_m1=None):
        if self.lp == 0:
            return self.eta * gradient 
        elif self.lp == 1:
            return self.eta * gradient + self.lmbda*anp.sign(theta_m1)
        elif self.lp == 2: 
            return self.eta * gradient + self.lmbda*theta_m1
        else:
            raise NotImplementedError('No method for lp > 2 has been implemented')
    
    def reset(self):
        return super().reset()


class MomentumGD(GDTemplate):
    def __init__(self, learning_rate=0.01,
                 momentum=0.0,
                 lmbda=0.0,
                 lp=0):
        super().__init__(learning_rate)
        self.mom = momentum
        self.lmbda = lmbda
        self.lp = lp

        
    def update_change(self, gradient, theta_m1):
        if self.lp == 0:
            return self.eta*gradient + self.mom*theta_m1
        elif self.lp == 1:
            return self.eta*gradient + self.mom*theta_m1 + self.lmbda*anp.sign(theta_m1)
        elif self.lp == 2: 
            return self.eta*gradient + self.mom*theta_m1 + self.lmbda*theta_m1
        else:
            raise NotImplementedError('No method for lp > 2 has been implemented')
    
    def reset(self):
        return super().reset()
    

class Adagrad(GDTemplate):
    def __init__(self, learning_rate=0.01,
                 momentum=0.0,
                 lmbda=0.0,
                 lp=0):
        
        super().__init__(learning_rate)
        self.mom = momentum
        self.adagrad_learn_rate = None
        self.lmbda = lmbda
        self.lp = lp

    def update_change(self, gradient,theta_m1):
        delta = 1e-7
        gradient2 = gradient*gradient
        self.adagrad_learn_rate = (self.eta)/(delta + anp.sqrt(gradient2))
        if self.lp == 0:
            return gradient*self.adagrad_learn_rate + self.mom*theta_m1
        elif self.lp == 1:
            return gradient*self.adagrad_learn_rate + self.mom*theta_m1 + self.lmbda*anp.sign(theta_m1)
        elif self.lp == 2:
            return gradient*self.adagrad_learn_rate + self.mom*theta_m1 + self.lmbda*theta_m1
        else:
            raise NotImplementedError('No method for lp > 2 has been implemented')
    
    def reset(self):
        self.adagrad_learn_rate = None


class RMSprop(GDTemplate):
    def __init__(self, learning_rate=0.01,
                 decay=0.9,
                 lmbda=0.0):
        super().__init__(learning_rate)
        self.rmsProp_update = 0.0
        self.decay = decay
        self.lmbda = lmbda

    def update_change(self, gradient, theta_m1):
        delta = 1e-8

        self.rmsProp_update = self.decay * self.rmsProp_update + (1 - self.decay)*gradient*gradient

        return self.eta/(anp.sqrt(self.rmsProp_update + delta)) * gradient + self.lmbda*theta_m1
    
    def reset(self):
        self.rmsProp_update = 0.0


class ADAM(GDTemplate):
    def __init__(self, learning_rate=0.01,
                 decay_rates=[0.9,0.99],
                 lmbda=0.0):
        super().__init__(learning_rate)
        self.decay1 = decay_rates[0]
        self.decay2 = decay_rates[1]
        self.lmbda = lmbda
        
        self.s = 0.0
        self.r = 0.0
        self.t = 1

    def update_change(self, gradient,theta_m1):
        delta = 1e-8

        self.s = self.decay1*self.s + (1. - self.decay1)*gradient
        self.r = self.decay2*self.r + (1. - self.decay2)*gradient*gradient

        s_corr = self.s / (1. - self.decay1**self.t)
        r_corr = self.r / (1. - self.decay2**self.t)

        return self.eta * (s_corr / (anp.sqrt(r_corr) + delta)) + self.lmbda*theta_m1
    
    def reset(self):
        self.s = 0.; self.r = 0.
        self.t += 1



## --- Plotting methods --- ##
def plot1D(x_data, z_data, labels=['','','','','',''],
           save=False, f_name: str='generic name.png'):
    """
    Returns a surface plot of 2D-data functions

    Parameters
    ---
    x_data : NDArray
        np.ndarray of x-axis data
    z_data : NDArray
        np.ndarray to be plotted against x_data
    labels : list
        List of figure labels. 0: axes-title; 1,2: x-,y-axis labels; 3: scatter-plot label; 4: line-plot label
    save : bool
        Default = False. Saves figure to current folder if True
    f_name : str
        file-name, including file-extension

    Returns
    ---
    Figure is initialized, must be shown explicitly

    """
    if save == True:
        plt.rcParams["font.size"] = 10
        fig,ax = plt.subplots(1,1,figsize=(3.5,(5*3/4)))
    else:
        fig,ax = plt.subplots(1,1)

    line_styles = [None,'--','-.']
    if type(z_data) == list:
        if len(labels) < 3 + len(z_data):
            for i in range(len(z_data)-2):
                labels.append('')
            print('Not enough labels, list extended with empty instances as:')
            print('labels =',labels)
   
    # Plotting initial data
    if type(z_data) != list:
        ax.plot(x_data,z_data,label=labels[3])
    else:
        ax.scatter(x_data,z_data[0],label=labels[3],color='0.15',alpha=0.65)
        for i in range(1,len(z_data)):
            ax.plot(x_data,z_data[i],label=labels[4+(i-1)],ls=line_styles[i-1])

    ax.set_title(labels[0]) 
    ax.set_xlabel(labels[1]); ax.set_ylabel(labels[2],rotation=0,labelpad=10)
    ax.legend(); ax.grid()
    if save == True:
        fig.savefig(f_name,dpi=300,bbox_inches='tight')

    return fig,ax

from mpl_toolkits.mplot3d import Axes3D
def plot2D(x_data, y_data, z_data, labels=['','','','','',''],
           colormap='viridis',
           save=False, f_name: str='generic name.png'
           ):
    """
    Returns a surface plot of 2D-data functions

    Parameters
    ---
    x_data : NDArray
        np.ndarray of x-axis data created with np.meshgrid(x,y)
    y_data : NDArray
        np.ndarray of y-axis data created with np.meshgrid(x,y)
    z_data : NDArray
        np.ndarray to be plotted on (x_data,y_data)-gird
    labels : list
        List of figure labels. 0: axes-title; 1,2,3: x-,y-, z-axis labels
    save : bool
        Default = False. Saves figure to current folder if True
    f_name : str
        file-name, including file-extension

    Returns
    ---
    Figure is initialized, must be shown explicitly

    """
    if save == True:
        plt.rcParams["font.size"] = 10
        fig = plt.figure(figsize=(4.5,(5*3/4)))
    else:
        fig = plt.figure()

    # Plotting initial data
    ax = fig.add_subplot(projection='3d')
    f1 = ax.plot_surface(x_data,y_data,z_data,cmap=colormap)
    ax.set_aspect(aspect='auto')

    ax.view_init(elev=30, azim=65)
    ax.set_title(labels[0]); ax.set_xlabel(labels[1])
    ax.set_ylabel(labels[2]); ax.set_zlabel(labels[3],rotation=90)
    ax.tick_params(axis='both', which='major', labelsize=6)
    fig.tight_layout(w_pad=10)
    if save == True:
        fig.savefig(f_name,dpi=300,bbox_inches='tight')

    return fig,ax

import matplotlib.colors as mcolors

def lambda_eta(data, axis_vals, axis_tick_labels=['',''],
               cbar_lim=[-10,10], cmap='viridis', 
               save=False, f_name='generic name.png'
               ):
    """
    Plotting a heatmap of input data using the Seaborn heatmap-method. 
    Default setup with axis-labels for comparing regression parameter λ- and learning rate, η.
    Plot can be modified by using the outputed fig,ax-objects with standard Matplotlib.pyplot-commands
    """
    if save == True:
        plt.rcParams["font.size"] = 10
        fig,ax = plt.subplots(1,1,figsize=(5,(5*3/4)))
    else:
        fig,ax = plt.subplots(1,1)
   
    mask = np.isnan(data)

    if len(axis_tick_labels) < 2: # Condition since we need tick-types for both axis, and only one is provided
      print('ListLengthWarning: Only one tick-label provided, using the same for 2nd axis')
      axis_tick_labels.append(axis_tick_labels)

    ax = sns.heatmap(data=data,vmin=cbar_lim[0],vmax=cbar_lim[1],cmap=cmap,annot=True,mask=mask,linecolor='0.5')
   
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            if mask[i, j]:
                ax.add_patch(plt.Rectangle((j, i), 1, 1, color='0.15', edgecolor='none'))
                ax.text(j + 0.5, i + 0.5, f"{data[i, j]:.1f}", ha='center', va='center', color="white")

    ax.set_xticks(np.arange(len(axis_vals[0])),labels=axis_tick_labels[0])
    ax.set_yticks(np.arange(len(axis_vals[1])),labels=axis_tick_labels[1],rotation=0)
    ax.set_xlabel('λ'); ax.set_ylabel('η',rotation=0,labelpad=10)

    if save == True:
        fig.savefig(f_name,dpi=300,bbox_inches='tight')
           
    return fig,ax

def contour_diff(x_data,y_data,z_data,cmap='viridis',
                 labels=['','',''],
                 save=False, f_name='generic_name.png'):
    """ Gives a contour plot based on `x_data`, `y_data` and `z_data`
        Labels: 0: Title; 1: x-axis label; 2; y-axis label

        Returns
        ---
        fig,ax : Modify with common pyplot-commands
    """
    
    
    if save == True:
        plt.rcParams["font.size"] = 10
        fig,ax = plt.subplots(1,1,figsize=(5,(5*3/4)))
    else:
        fig,ax = plt.subplots(1,1)

    f = ax.contourf(x_data,y_data,z_data,levels=15,cmap=cmap)
    ax.set_title(labels[0]); ax.set_xlabel(labels[1]); ax.set_ylabel(labels[2],rotation=0)
    fig.colorbar(f)

    if save == True:
        fig.savefig(f_name,dpi=300,bbox_inches='tight')

    return fig,ax

def rand_heatmap(data,axis_vals,axis_tick_labels='float',axis_labels=['x','y'],
                 bin_vals=4,
                 cbar_lim=[-10,10], cmap='viridis', 
                 save=False, f_name='generic name.png'):
    """ Returns a heatmap based of the `data`-values, based on the values in `axis_vals`, 
        assuming `axis_vals` are picked randomly from a distribution. 
        
        Creates bins for the heatmap based on the min and max values of `axis_vals`, the number
        of bins is `binvals`-1

        Returns
        ---
        fig,ax as pyplot-objects for modification 
        
    """
    
    #x_bins = np.linspace( min(axis_vals[0]),max(axis_vals[0]), bin_vals )
    x_bins = np.linspace( np.nanmin(axis_vals[0]),np.nanmax(axis_vals[0]), bin_vals )

    #y_bins = np.linspace( min(axis_vals[1]),max(axis_vals[1]), bin_vals )
    y_bins = np.linspace( np.nanmin(axis_vals[1]),np.nanmax(axis_vals[1]), bin_vals )


    grid_data = np.zeros( ( len(x_bins)-1, len(y_bins)-1 ) )

    for i in range(len(x_bins)-1):
        for j in range(len(y_bins)-1):
            # Find indices of points within the current grid cell
            in_bin = (
                (axis_vals[0] >= x_bins[i]) & (axis_vals[0] < x_bins[i+1]) &
                (axis_vals[1] >= y_bins[j]) & (axis_vals[1] < y_bins[j+1])
            )
            if np.any(in_bin):
                grid_data[i,j] = np.min(data[in_bin])
            else:
                grid_data[i,j] = np.nan
    
    if save == True:
        plt.rcParams["font.size"] = 10
        fig,ax = plt.subplots(1,1,figsize=(5,(5*3/4)))
    else:
        fig,ax = plt.subplots(1,1)
   
    mask = np.isnan(grid_data)

    if len(axis_tick_labels) < 2: # Condition since we need tick-types for both axis, and only one is provided
        print('ListLengthWarning: Only one tick-label provided, using the same for 2nd axis')
        axis_tick_labels.append(axis_tick_labels)
    
    cbar_lim = [np.nanmin(grid_data),np.nanmax(grid_data)]

    ax = sns.heatmap(data=grid_data,
                     vmin=cbar_lim[0],vmax=cbar_lim[1],
                     cmap=cmap,annot=True,mask=mask,linecolor='0.5')
   
    for i in range(grid_data.shape[0]):
        for j in range(grid_data.shape[1]):
            if mask[i, j]:
                ax.add_patch(plt.Rectangle((j, i), 1, 1, color='1', edgecolor='none'))
                ax.text(j + 0.5, i + 0.5, f"{grid_data[i, j]:.1f}", ha='center', va='center', color="white")

    ## Setting up ticks
    if axis_tick_labels == 'float':
        x_ticks = [f'{y:.0f}' for y in x_bins]
        y_ticks = [f'{y:.0f}' for y in y_bins]
    elif axis_tick_labels == 'scientific':
        x_ticks = [f'{y:.0e}' for y in x_bins]
        y_ticks = [f'{y:.0e}' for y in y_bins]
    else:
        x_ticks = [f'{y:i}' for y in x_bins]
        y_ticks = [f'{y:i}' for y in y_bins]

    ax.set_xticks(np.arange(len(x_bins)),labels=x_ticks)
    ax.set_yticks(np.arange(len(y_bins)),labels=y_ticks,rotation=0)

    ax.set_xlabel(axis_labels[0]); ax.set_ylabel(axis_labels[1],rotation=0,labelpad=10)
    ax.set_title('Random grid search\nBest cost: %.3e' %data[data.argmin()])

    if save == True:
        fig.savefig(f_name,dpi=300,bbox_inches='tight')
    
    return fig,ax

def rand_scatter(data,axis_vals=[None,None],axis_labels=['x','y'],
                cbar_lim=[-10,10], cmap='magma', 
                save=False, f_name='generic name.png'):
    """ Creates a scatter plot for the values after a random grid search, 
        highlighting the best score (min of `data`) with a star. 
        
        Coloring of markers are based on `data`, positions on `axis_vals`

        Returns
        ---
        fig,ax : as pyplot-objects for modification    
    """

    min_idx = np.argmin(data)

    fig,ax = plt.subplots(1,1)
    f = ax.scatter(axis_vals[0],axis_vals[1],c=data,cmap=cmap,vmin=cbar_lim[0],vmax=cbar_lim[1])
    ax.scatter(axis_vals[0][min_idx], axis_vals[1][min_idx], color='C3', edgecolor='C8', s=200, marker='*', label='Min Value')
    cbar = fig.colorbar(mappable=f)
    cbar.set_label('Cost value')

    ax.set_xlabel(axis_labels[0]); ax.set_ylabel(axis_labels[1],rotation=0,labelpad=10)
    #ax.legend()
    ax.set_title((f'Best cost = {data[min_idx] :.5e}\n{axis_labels[0]} , {axis_labels[1]} = '+
                 f'{axis_vals[0][min_idx] :.2e} , {axis_vals[1][min_idx] :.2e}'))

    return fig,ax



# ---- UNUSED ---- #
def rand_scatter3d(data,axis_vals):
    from mpl_toolkits.mplot3d import Axes3D

    fig = plt.figure()
    ax = fig.add_subplot(111,projection='3d')
    sc = ax.scatter(axis_vals[0],axis_vals[1],data,c=data,cmap='magma',edgecolors='k')

    fig.colorbar(mappable=sc)

    return fig,ax


def rand_contour(data,axis_vals):
    from scipy.interpolate import griddata

    x_grid,y_grid = np.meshgrid(axis_vals[0],axis_vals[1])

    grid_data = griddata(points=(axis_vals[0],axis_vals[1]),values=data, xi=(x_grid,y_grid),method='linear')

    fig,ax = plt.subplots(1,1)
    f = ax.contourf(x_grid,y_grid,grid_data,levels=10)
    fig.colorbar(mappable=f)

    return fig,ax