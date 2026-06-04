from kivy.garden.graph import Graph, MeshLinePlot

def update_graph(self, user, month=None, year=None):
    self.graph_box.clear_widgets()
    
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    query = "SELECT category, SUM(amount) FROM expenses WHERE username=?"
    params = [user]
    if month:
        query += " AND strftime('%m', date_added) = ?"
        params.append(month.zfill(2))
    if year:
        query += " AND strftime('%Y', date_added) = ?"
        params.append(year)
    query += " GROUP BY category"
    cursor.execute(query, params)
    data = cursor.fetchall()
    conn.close()

    if not data:
        return

    labels = [row[0] for row in data]
    amounts = [float(row[1]) for row in data]

    graph = Graph(
        xlabel='Category',
        ylabel='Amount ($)',
        x_ticks_minor=5,
        x_ticks_major=1,
        y_ticks_major=1,
        y_grid_label=True,
        x_grid_label=True,
        padding=5,
        xlog=False,
        ylog=False,
        x_grid=True,
        y_grid=True,
        xmin=-1,
        xmax=len(labels),
        ymin=0,
        ymax=max(amounts) * 1.2 if amounts else 10
    )
    graph.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
    graph.size_hint = (1, 1)

    # Bar chart
    if self.current_graph_type == "bar":
        for i, amt in enumerate(amounts):
            bar = MeshLinePlot(color=[0.27, 0.72, 0.82, 1])
            bar.points = [(i, 0), (i, amt)]
            graph.add_plot(bar)
    # Line chart
    elif self.current_graph_type == "line":
        line = MeshLinePlot(color=[1, 0.42, 0.42, 1])
        line.points = [(i, amt) for i, amt in enumerate(amounts)]
        graph.add_plot(line)
    # Pie chart fallback to bar
    else:
        for i, amt in enumerate(amounts):
            bar = MeshLinePlot(color=[0.27, 0.72, 0.82, 1])
            bar.points = [(i, 0), (i, amt)]
            graph.add_plot(bar)

    self.graph_box.add_widget(graph)
