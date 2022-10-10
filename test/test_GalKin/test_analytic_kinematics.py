import pytest
from lenstronomy.GalKin.analytic_kinematics import AnalyticKinematics
import numpy as np
from lenstronomy.GalKin.numeric_kinematics import NumericKinematics
from astropy.cosmology import FlatLambdaCDM
import numpy.testing as npt


class TestAnalyticKinematics(object):

    def setup(self):
        pass

    def test_sigma_s2(self):
        kwargs_aperture = {'center_ra': 0, 'width': 1, 'length': 1, 'angle': 0, 'center_dec': 0,
                           'aperture_type': 'slit'}
        kwargs_cosmo = {'d_d': 1000, 'd_s': 1500, 'd_ds': 800}
        kwargs_psf = {'psf_type': 'GAUSSIAN', 'fwhm': 1}
        kin = AnalyticKinematics(kwargs_cosmo, interpol_grid_num=2000,
                                 log_integration=True, max_integrate=100,
                                 min_integrate=5e-6)
        kwargs_light = {'r_eff': 1}
        sigma_s2 = kin.sigma_s2(r=1, R=0.1, kwargs_mass={'theta_E': 1, 'gamma': 2}, kwargs_light=kwargs_light,
                                kwargs_anisotropy={'r_ani': 1})
        npt.assert_almost_equal(sigma_s2[0], 70885880558.5913, decimal=3)

    def test_against_numeric_profile(self):
        z_d = 0.295
        z_s = 0.657

        kwargs_model = {
            'mass_profile_list': ['PEMD'],
            'light_profile_list': ['HERNQUIST'],
            'anisotropy_model': 'OM',
            # 'lens_redshift_list': [z_d],
        }

        cosmo = FlatLambdaCDM(H0=70, Om0=0.3)
        D_d = cosmo.angular_diameter_distance(z_d).value
        D_s = cosmo.angular_diameter_distance(z_s).value
        D_ds = cosmo.angular_diameter_distance_z1z2(z_d, z_s).value

        kwargs_cosmo = {'d_d': D_d, 'd_s': D_s, 'd_ds': D_ds}

        numeric_kin = NumericKinematics(kwargs_model, kwargs_cosmo,
                                        interpol_grid_num=1000,
                                        max_integrate=1000, min_integrate=1e-4)
        analytic_kin = AnalyticKinematics(kwargs_cosmo,
                                          interpol_grid_num=2000,
                                          max_integrate=100,
                                          min_integrate=1e-4)

        R = np.logspace(-5, np.log10(6), 100)
        r_eff = 1.85
        theta_e = 1.63
        gamma = 2
        a_ani = 1

        numeric_s2ir, numeric_ir = numeric_kin.I_R_sigma2_and_IR(R,
                                                                 [{
                                                                      'theta_E': theta_e,
                                                                      'gamma': gamma,
                                                                      'center_x': 0.,
                                                                      'center_y': 0.}],
                                                                 [{
                                                                      'Rs': r_eff * 0.551,
                                                                      'amp': 1.,
                                                                      'center_x': 0.,
                                                                      'center_y': 0.}],
                                                                 {
                                                                     'r_ani': a_ani * r_eff})

        numeric_vel_dis = np.sqrt(numeric_s2ir / numeric_ir) / 1e3

        analytic_s2ir = np.zeros_like(R)
        analytic_ir = np.zeros_like(R)

        for i, r in enumerate(R):
            analytic_s2ir[i], analytic_ir[i] = analytic_kin.I_R_sigma2_and_IR(
                r,
                {'theta_E': theta_e, 'gamma': gamma, 'center_x': 0.,
                 'center_y': 0.},
                {'Rs': r_eff * 0.551, 'amp': 1., 'center_x': 0.,
                 'center_y': 0.},
                {'r_ani': a_ani * r_eff})

        analytic_vel_dis = np.sqrt(analytic_s2ir / analytic_ir) / 1e3

        # check if matches below 1%
        npt.assert_array_less((numeric_vel_dis -
                               analytic_vel_dis)/numeric_vel_dis,
                               0.01*np.ones_like(numeric_vel_dis))


if __name__ == '__main__':
    pytest.main()
