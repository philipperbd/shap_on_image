from matplotlib import pyplot as plt
import matplotlib.cm as cm
import os
import cv2
from shap_on_image.utils import *
import numpy as np


class ShapOnImageAuto:

    def __init__(self, image, features, values, shap, stats, positions={}):
        """
        args:
            image: str, path to image
            features: list, features names as strings
            shap: list, shap values extracted from shap packages
            positions: dict, features with 'x' and 'y' values, can be set with set_positions()
        """
        try:
            os.path.exists(image)
            self.image = image
            self.features = features
            self.values = values
            self.shap = shap
            self.stats = stats
            self.positions = positions
            self.feature_cnt = 0
        except:
            print('Error during init - verify path to image')

    def set_positions(self):
        """
        Tool to select positions of every feature on the image.
        """
        if not hasattr(self, 'image'):
            print('No image loaded yet - use get_image() function')
        else:
            img = cv2.imread(self.image, 1)
            cv2.imshow('image', img)
            ask_for_feature(self)
            cv2.setMouseCallback('image', click_event, [self, img])
            cv2.waitKey(0)

    def get_positions(self):
        """
        Return list of positions
        """
        return self.positions

    def create_plot(self, path, plot_name, suptitle, title, sym, full_plt=True, alpha=1):
        """
        Plot the figure with image and shap values at specific positions
        args:
            suptitle: str, suptitle to display on image
            title: str, title to display on image
            alpha: float, coefficient to multiply every shap values by.
        """
        im = plt.imread(self.image)
        fig, ax = plt.subplots()
        im = ax.imshow(im)
        plt.axis('off')

        plt.suptitle(suptitle, weight="bold")
        plt.title(title)

        shap_dataset = self.shap[plot_name]  # d[name]

        features = [feature for feature in shap_dataset.keys()]

        x = [self.positions[feature]['x'] for feature in features]
        y = [self.positions[feature]['y'] for feature in features]

        
        color = [
            feature_color(plot_name, feature, self.values)
            for feature in shap_dataset.keys()]

        
        if full_plt:
            plt.title(title[0] + title[1])

            shap_values = [shap_value *
                       alpha for shap_value in shap_dataset.values()]
            plt.scatter(x, y, s=shap_values, c=color, cmap=cm.bwr, label='shap')

            arr_pos = [self.positions["Arrow"]["x"], self.positions["Arrow"]["x"]]
            plt.arrow(
                x=arr_pos[0], y=arr_pos[1], 
                dx=0, dy=-1 * np.sign(sym[0]) * (np.abs(sym[0]) - 1) * 20, 
                head_width=5, color="purple")  # top / bot
            plt.arrow(
                x=arr_pos[0], y=arr_pos[1], 
                dx=np.sign(sym[1]) * (np.abs(sym[1]) - 1) * 20, dy=0, 
                head_width=5, color="purple")  # left / right
        else:
            plt.title(title[0])
            plt.scatter(x, y, s=30, c=color, cmap=cm.bwr, label='shap')

        plt.close(fig)
        fig.savefig(path + plot_name + '.png', dpi=500)

    def create_plot_linear(self, path, plot_name, suptitle, title, sym, alpha=1):
        """
        Plot the figure with image and shap values at specific positions
        args:
            suptitle: str, suptitle to display on image
            title: str, title to display on image
            alpha: float, coefficient to multiply every shap values by.
        """
        im = plt.imread(self.image)
        fig, ax = plt.subplots()
        im = ax.imshow(im)
        plt.axis('off')

        plt.suptitle(suptitle, weight="bold")
        plt.title(title)

        for feature, shap_value in self.shap[plot_name].items():
            shap = shap_value * alpha
            #color = feature_color(plot_name, feature, self.values)
            color = "green"

            if feature == "Face":
                x = self.positions[feature]['x']
                y = self.positions[feature]['y']
                plt.scatter(x, y, s=abs(shap), c=color)

            else:
                feature_type = feature[-2:]
                x = self.positions[feature[:-2]]['x']
                y = self.positions[feature[:-2]]['y']
                shap = shap / 3

                if feature_type == '_x':
                    plt.plot([x - abs(shap)/2, x + abs(shap)/2],
                             [y, y], c=color)
                else:
                    plt.plot([x, x], [y - abs(shap)/2,
                             y + abs(shap)/2], c=color)

        arr_pos = [self.positions["Arrow"]["x"], self.positions["Arrow"]["x"]]

        plt.arrow(
            x=arr_pos[0], y=arr_pos[1], 
            dx=0, dy=-(sym[0]-1)*20, 
            head_width=5, color="purple") # top / bot
        plt.arrow(
            x=arr_pos[0], y=arr_pos[1], 
            dx=(sym[1]-1)*20, dy=0, 
            head_width=5, color="purple") # left / right

        plt.close(fig)
        fig.savefig(path + plot_name + '.png', dpi=500)

    def create_plots(self, path="", full_plt=True, alpha=1):
        """Create several plots and save them in path.

        Args:
            path (str, optional): Path to output plots. Defaults to "".
            alpha (int, optional): Coefficient to multiply shap values by. Defaults to 1.
        """
        for plot_name, _ in self.shap.items():
            suptitle, title, sym = informations(
                self, plot_name=plot_name, stats=self.stats)
            if plot_name[:11] == 'linear_data':
                self.create_plot_linear(
                    path=path, plot_name=plot_name,
                    suptitle=suptitle, title=title,
                    sym=sym, alpha=alpha)
            else:
                self.create_plot(
                    path=path, plot_name=plot_name,
                    suptitle=suptitle, title=title,
                    sym=sym, full_plt=full_plt, alpha=alpha)
