__author__ = 'aleaf'

import numpy as np
import pandas as pd
import fiona
from shapely.geometry import mapping, shape, Point


def point_shapefile(df, X, Y, shpname, prj=None):

    df['geometry'] = [Point(r[X], r[Y]) for i, r in df.iterrows()]

    Shapefile(df, shpname, prj)


def read_shapefile(shapefile, index=None, true_values=None, false_values=None, \
           skip_empty_geom=True):
    '''
    Read shapefile into Pandas dataframe
    ``shplist`` = (string or list) of shapefile name(s)
    ``index`` = (string) column to use as index for dataframe
    ``geometry`` = (True/False) whether or not to read geometric information
    ``clipto`` = (dataframe) limit what is brought in to items in index of clipto (requires index)
    ``true_values`` = (list) same as argument for pandas read_csv
    ``false_values`` = (list) same as argument for pandas read_csv
    from shapefile into dataframe column "geometry"
    '''

    print "\nreading {}...".format(shapefile)
    shp_obj = fiona.open(shapefile, 'r')

    if index is not None:
        # handle capitolization issues with index field name
        fields = shp_obj.schema['properties'].keys()
        index = [f for f in fields if index.lower() == f.lower()][0]

    attributes = []
    for line in shp_obj:

        props = line['properties']
        props['geometry'] = line.get('geometry', None)
        attributes.append(props)

    print '--> building dataframe... (may take a while for large shapefiles)'
    df = pd.DataFrame(attributes)

    # handle null geometries
    geoms = df.geometry.tolist()
    if geoms.count(None) == 0:
        df['geometry'] = [shape(g) for g in geoms]
    elif skip_empty_geom:
        null_geoms = [i for i, g in enumerate(geoms) if g is None]
        df.drop(null_geoms, axis=0, inplace=True)
        df['geometry'] = [shape(g) for g in df.geometry.tolist()]
    else:
        df['geometry'] = [shape(g) if g is not None else None
                              for g in geoms]

    # set the dataframe index from the index column
    if index is not None:
        df.index = df[index].values

    # convert any t/f columns to numpy boolean data
    if true_values or false_values:
        replace_boolean = {}
        for t in true_values:
            replace_boolean[t] = True
        for f in false_values:
            replace_boolean[f] = False

        # only remap columns that have values to be replaced
        for c in df.columns:
            if len(set(df[c]).intersection(set(true_values))) > 0:
                df[c] = df[c].map(replace_boolean)
    return df


class Shapefile:

    def __init__(self, df, shpname, geo_column='geometry', prj=None):

        self.df = df
        self.shpname = shpname
        self.geo_column = geo_column
        self.prj = prj

        self.geomtype = self.df.iloc[0][self.geo_column].type

        # make the shapefile
        self.limit_fieldnames()
        self.convert_dtypes()
        self.write()
        self.set_projection()

    def convert_dtypes(self):
        """convert data-types and data-type names to comply with shapefile format

        Returns
        -------
        dictionary of {columns (str) : properties (str)}
        """
        i = -1
        dtypes = list(self.df.dtypes)
        for dtype in dtypes:
            i += 1
            if dtype == np.dtype('float64'):
                continue
            # not sure if this is needed
            #elif 'float' in dtype.name:
            #    df[df.columns[i]] = df[df.columns[i]].astype('float64')
            # convert 64-bit integers to 32-bit for shapefile format
            elif dtype == np.dtype('int64'):
                self.df[self.df.columns[i]] = self.df[self.df.columns[i]].astype('int32')
            # convert boolean values to strings
            elif dtype == np.dtype('bool'):
                self.df[self.df.columns[i]] = self.df[self.df.columns[i]].astype('str')

        # strip dtype names just down to 'float' or 'int'
        dtypes = [''.join([c for c in d.name if not c.isdigit()]) for d in list(self.df.dtypes)]

        # also exchange any 'object' dtype for 'str'
        dtypes = [d.replace('object', 'str') for d in dtypes]
        self.properties = dict(zip(self.df.columns, dtypes))

        # delete the geometry column
        del self.properties[self.geo_column]

    def limit_fieldnames(self):
        """limit field names to ESRI 10-character maximum
        """
        self.df.columns = map(str, self.df.columns) # convert columns to strings in case some are ints
        overtheline = [(i, '{}{}'.format(c[:8], i)) for i, c in enumerate(self.df.columns) if len(c) > 10]

        newcolumns = list(self.df.columns)
        for i, c in overtheline:
            newcolumns[i] = c
        self.df.columns = newcolumns

    def write(self):
        '''save dataframe with column of shapely geometry objects to shapefile
        '''
        print 'writing {}...'.format(self.shpname)

        # sort the dataframe columns (so that properties coincide)
        self.df = self.df.sort(axis=1)


        schema = {'geometry': self.geomtype, 'properties': self.properties}
        knt = 0
        length = len(self.df)
        problem_cols = []
        with fiona.collection(self.shpname, "w", "ESRI Shapefile", schema) as output:
            for i in range(length):
                geo = self.df.iloc[i][self.geo_column]

                # convert numpy ints to python ints (tedious!)
                props = {}
                for c in range(len(self.df.columns)):
                    value = self.df.iloc[i][c]
                    col = self.df.columns[c]
                    #print i,c,col,value
                    dtype = self.df[col].dtype.name
                    #dtype = self.df.iloc[c].dtype.name
                    if col == self.geo_column:
                        continue
                    else:
                        try:
                            if 'int' in dtype:
                                props[col] = int(value)
                            #elif 'float' in dtype:
                                #props[col] = np.float64(value)
                            elif schema['properties'][col] == 'str' and dtype == 'object':
                                props[col] = str(value)
                            else:
                                props[col] = value
                        except AttributeError: # if field is 'NoneType'
                            problem_cols.append(col)
                            props[col] = ''

                output.write({'properties': props,
                              'geometry': mapping(geo)})
                knt +=1
                print '\r{:d}%'.format(100*knt/length),


        if len(problem_cols) > 0:
            print 'Warning: Had problems writing these DataFrame columns: {}'.format(problem_cols)
            print 'Check their dtypes.'

    def set_projection(self):
        if self.prj:
            if 'epsg' in self.prj.lower():
                self.epsg = int(self.prj.split(':')[1])
                self.getPRJwkt()
                ofp = open("{}.prj".format(self.shpname[:-4]), 'w')
                ofp.write(self.prettywkt)
                ofp.close()
            else:
                try:
                    self.shutil.copyfile(self.prj, "{}.prj".format(self.shpname[:-4]))
                except IOError:
                    print 'Warning: could not find specified prj file. shp will not be projected.'

    def getPRJwkt(self):
        """
        from: https://code.google.com/p/pyshp/wiki/CreatePRJfiles

        Grabs a WKT version of an EPSG code
        usage getPRJwkt(4326)

        This makes use of links like http://spatialreference.org/ref/epsg/4326/prettywkt/
        """
        import urllib
        f = urllib.urlopen("http://spatialreference.org/ref/epsg/{0}/prettywkt/".format(self.epsg))
        self.prettywkt = f.read().replace('\n', '') # get rid of any EOL


class PyShpfile(Shapefile):

    def __init__(self, df, X, Y, shpname, prj=None):

        Shapefile.__init__(self, df, X, Y, shpname, prj=None)

        self.X = X
        self.Y = Y
        self.fields = df.columns.drop([X, Y])

    # function to write out results to csv file
    def writeout_shp(self, cshp, X, Y, cname, res,resplot,meas,mod,c_rpd):
        cshp.point(X,Y)
        cshp.record(name=cname,residual=res,plot_res=resplot,meas=meas,modeled=mod,rpd=c_rpd)
        return cshp

    # initialize the shapefile object with fields
    def init_shp(self):
        for cf in fields:
            # make the name field of character type
            if 'name' in cf.lower():
                cshp.field(cf)
            # the other fields should be numeric
            else:
                cshp.field(cf,fieldType='N',size='50',decimal=8)

        return cshp