import math

class Fiber:
    """Functions specifc to individual fibers whose data has already been processed by process_DTI.

    Methods
    -------
    getFsds(ecs)
        Get first spatial derivative of EC potentials at Nodes of Ranvier.
    getSsds(ecs)
        Get second spatial derivative of EC potentials at Nodes of Ranvier.
    getCenterInd(centering_strategy, number_of_spatial_values=11)
        Get the index of the center node of a fiber. Corresponds to site of initiation of action potential.
    getValAroundCenterNode(type, vals, num_vals, center_ind)
        Get values around the center node of a given type (ec, fsd, ssd, err).
    """

    def __init__(self, ecs):
        """
        Parameters
        ----------
        ecs: list
            A list of EC potentials at Nodes of Ranvier.

        Attributes
        ----------
        ecs: list
            EC potentials at Nodes of Ranvier.
        fsds: list
            First spatial derivatives (fsds) of EC potentials.
        ssds: list
            Second spatial derivatives (ssds) of EC potentials.
        isValidCenterInd: bool
            Flag to determine if the center node is valid.
        site_of_initiation: int
            Index of the center node of the fiber.
        """
        self.ecs = ecs
        self.fsds = self.getFsds(ecs)
        self.ssds = self.getSsds(ecs)

        self.isValidCenterInd = None
        self.site_of_initiation = None

    def getFsds(self, ecs: list, truncated=False) -> list:
        """Get first spatial derivative of EC potentials at Nodes of Ranvier for a given fiber.

        This function computes the first spatial derivative (fsds) of EC potentials
        for all nodes except the first and last nodes, which do not have a first derivative.

        Parameters
        ----------
        ecs: list
            A list of EC potentials at Nodes of Ranvier. None values are used to indicate the
            first and last nodes of the fiber which do not have a first spatial derivative.
            None values are left in to maintain the same indices as the original list of EC potentials.
            This is important for centering values around index w/ site of initiation of action potential.
        truncated: bool
            If True, the first and last elements of the fsds list will be removed.

        Returns
        -------
        list
            A list of first spatial derivatives (fsds) of EC potentials with None for the 
            first and last nodes to maintain index alignment.
        """
        fsds = [None]*len(ecs)

        for i in range(1,len(ecs)-1):
            fsd = self.__getFsd(ecs[i-1], ecs[i+1])
            fsds[i] = fsd
        
        fsds = fsds[1:-1] if truncated else fsds

        return fsds

    def getSsds(self, ecs: list, truncated=False) -> list:
        """Get second spatial derivative of EC potentials at Nodes of Ranvier for a given fiber.

        This function computes the second spatial derivative (ssds) of EC potentials
        for all nodes except the first and last nodes, which do not have a second derivative.

        Parameters
        ----------
        ecs: list
            A list of EC potentials at Nodes of Ranvier. None values are used to indicate the
            first and last nodes of the fiber which do not have a second spatial derivative.
            None values are left in to maintain the same indices as the original list of EC potentials.
            This is important for centering values around index w/ site of initiation of action potential.
        truncated: bool
            If True, the first and last elements of the ssds list will be removed.

        Returns
        -------
        list
            A list of second spatial derivatives (ssds) of EC potentials with None for the 
            first and last nodes to maintain index alignment.
        """
        ssds = [None]*len(ecs)

        for i in range(1,len(ecs)-1):
            ssd = self.__getSsd(ecs[i], ecs[i-1], ecs[i+1])
            ssds[i] = ssd

        ssds = ssds[1:-1] if truncated else ssds

        return ssds

    def getCenterInd(self, centering_strategy, number_of_spatial_values=11):
        """Get the index of the center node of a fiber. Corresponds to site of initiation of action potential.

        This function determines the index of the center node of a fiber based on the
        extracellular potentials (ecs) at the nodes of Ranvier. The centering strategy
        determines the method used to determine the center node. The number of spatial
        values determines the number of values to center around the center node.

        Parameters
        ----------
        centering_strategy: str
            The strategy to use to center the fiber (ssd, ec).
        number_of_spatial_values: int
            The number of spatial values to center around the center node.

        Returns
        -------
        int
            The index of the center node of the fiber.
        """
        center_ind = 0
        input_bound = math.floor(number_of_spatial_values / 2)
        ssds = self.ssds
        ecs = self.ecs

        # return maximum second spatial derivative index, which corresponds to site of initiation of action potential
        if centering_strategy == "ssd":
            max_ssd = max(ssds[1:-1])
            max_ssd_ind = ssds.index(max_ssd)
            center_ind = max_ssd_ind

        # return minimum extracellular voltage index, which corresponds to site of initiation of action potential
        elif centering_strategy == "ec":
            min_ec = min(ecs)
            min_ec_ind = ecs.index(min_ec)
            center_ind = min_ec_ind

        # center of sent in data (min_ecs or max_ssd) is too close to the edge of the fiber
        if (center_ind < input_bound + 1 or len(ecs) - 1 - center_ind < input_bound + 1):
            self.isValidCenterInd = False
        else:
            self.isValidCenterInd = True

        self.site_of_initiation = center_ind
        return center_ind

    def getValAroundCenterNode(self, spatial_derivative_type, num_vals, center_ind):
        """Get values around the center node of a given type (ec, fsd, ssd, err).

        This function returns a list of values around the center node of a fiber. The number of values
        returned is determined by the num_vals parameter. The type parameter determines the type of
        values to return (ec, fsd, ssd, err).

        Parameters
        ----------
        type: str
            The type of values to return (ec, fsd, ssd, err).
        vals: list
            A list of values to center around the center node.
        num_vals: int
            The number of values to return around the center node.
        center_ind: int
            The index of the center node of the fiber.

        Returns
        -------
        list
            A list of values centered around the center node of the fiber.
        """
        if num_vals == 0:
            return []

        vals_lower_bound = center_ind - (math.floor(num_vals / 2))
        vals_upper_bound = center_ind + (math.floor(num_vals / 2)) + 1

        if spatial_derivative_type == "ec":
            return self.ecs[vals_lower_bound:vals_upper_bound]
        elif spatial_derivative_type == "fsd":
            result = self.fsds[vals_lower_bound:vals_upper_bound]
            # Filter out None values from boundaries (fsds has None at index 0 and -1)
            return [val if val is not None else 0.0 for val in result]
        elif spatial_derivative_type == "ssd":
            result = self.ssds[vals_lower_bound:vals_upper_bound]
            # Filter out None values from boundaries (ssds has None at index 0 and -1)
            return [val if val is not None else 0.0 for val in result]
        elif spatial_derivative_type == "err":
            return [0 for err in range(num_vals)]

    def __getSsd(self, ec_0, ec_prev, ec_nxt):
        return ec_prev - (2*ec_0) + ec_nxt

    def __getFsd(self, ec_prev, ec_nxt):
        return (ec_nxt - ec_prev) / 2