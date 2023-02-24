from matplotlib import pyplot as plt
import os
import cv2
from shap_on_image.utils import *

class ShapOnImageAuto:

    def __init__(self, image, features, shap, auc, positions={}):
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
            self.shap = shap 
            self.auc = auc
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

    def symmetry(self, plot_name):
        """
        return value of symmetry for top/bot and left/right
        """
        check_list_top = ['shoulder', 'elbow', 'wrist', 'top']
        check_list_right = ['rshoulder', 'relbow', 'rwrist', 'rhip', 'rknee', 'rankle', 'right']
        
        top, bot, right, left = [], [], [], []
        
        for feature, shap_value in self.shap[plot_name].items():
            for word in check_list_top:
                if word in feature.lower(): top.append(shap_value)
                else: bot.append(shap_value)
            for word in check_list_right:
                if word in feature.lower(): right.append(shap_value)
                else: left.append(shap_value)
        
        print(plot_name, sum(top), sum(bot), sum(right), sum(left))

        top, bot, right, left = sum(top), sum(bot), sum(right), sum(left)
        
        if bot > top:
            sym_top_bot = round(bot / top)
        else:
            sym_top_bot = round(top / bot) * -1
        
        if left > right:
            sym_left_right = round(left / right)
        else:
            sym_left_right = round(right / left) * -1

        return sym_top_bot, sym_left_right

    def create_plot(self, path, plot_name, suptitle="", title="", alpha=1):
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

        try:
            dataset = plot_name.rsplit('_', 1)[0]
            auc = self.auc[dataset]['mean']
            std = self.auc[dataset]['std']
        except:
            auc = 00
            std = 00

        plt.suptitle(plot_name.replace('_', ' ').upper(), weight="bold")
        plt.title('XGBoost mean AUC : ' + str(auc) + ' ('+ str(std) + ')')

        for feature, shap_value in self.shap[plot_name].items():
            try:
                shap = shap_value * alpha
                x = self.positions[feature]['x']
                y = self.positions[feature]['y']
                color = ["cornflowerblue" if shap > 0 else "crimson"]
                plt.scatter(x, y, s=abs(shap), color=color)
            except:
                print(plot_name, feature)

        sym_top_bot, sym_left_right = self.symmetry(plot_name=plot_name)
        plt.arrow(400, 410, sym_left_right * 3, 0, head_width=5, color="crimson")
        plt.arrow(400, 410, 0, sym_top_bot * 3, head_width=5, color="crimson")

        plt.close(fig)
        fig.savefig(path + plot_name + '.png')

    def create_plots(self, path = "", alpha=1):
        """Create several plots and save them in path.

        Args:
            path (str, optional): Path to output plots. Defaults to "".
            alpha (int, optional): Coefficient to multiply shap values by. Defaults to 1.
        """
        for plot_name, _ in self.shap.items():
            #print(plot_name)
            self.create_plot(path, plot_name, alpha=alpha)
        
        